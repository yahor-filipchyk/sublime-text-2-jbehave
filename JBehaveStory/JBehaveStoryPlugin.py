import sublime, sublime_plugin
import os
import re
import webbrowser
from subprocess import Popen, PIPE
import threading
import sys
import time

PROJECT_FOLDER = "C:\\th" if "win" in sys.platform else "/th"
STEPS_FOLDER = "src{0}main{0}java{0}com{0}thunderhead{0}juice{0}integration{0}jbehave{0}steps".format(os.sep)
MAVEN_FOLDER = PROJECT_FOLDER + "{0}apps{0}apache-maven-3.1.0{0}bin".format(os.sep)
MAVEN_SETTINGS = PROJECT_FOLDER + "{0}apps{0}apache-maven-3.1.0{0}conf{0}settings.xml".format(os.sep)

JIRA_BROWSE = "https://thunderhead.jira.com/browse/"

STORY_FOLDER = "story.folder"
STORY_FILTER = "story.filter"
TEST_URI = "test.uri"
LOCAL = "local"
XQADEV = "xqadev"
XSTAGING = "xstaging"
XDEVTINY = "xdevtiny"
TINY10_PORT = 4443

DEFAULT_URLS = {
	LOCAL: "https://www.thxcloud.com",
	XQADEV: "https://xqadev.thunderhead.com",
	XSTAGING: "https://xstaging.thunderhead.com",
	XDEVTINY: "https://xdevtiny{0}.thunderhead.com",
}

DEFAULT_CONFIG = {
	STORY_FOLDER: "",
	STORY_FILTER: "",
	TEST_URI: XQADEV,
}

AUTOMATION_RUN = None


def does_story_step_match_actual(story_step, actual_step):
	step_pattern = get_step_pattern(actual_step)
	return story_step == actual_step or re.match(step_pattern, story_step) is not None


def get_step_pattern(step):
	params = re.findall(r'\s?(\$\w+|<\w+>)\s?', step)
	step_pattern = str(step)
	for param in params:
		step_pattern = re.sub(re.escape(param), '(.*)', step_pattern, 1)
	# composite steps handling
	if re.match(r'.*: \(\.\*\).*', step_pattern):
		step_pattern = re.sub(r' \(\.\*\)', '(.*)', step_pattern)
	return step_pattern

def get_automation_folder(current_file):
	match = re.search(r'(.*juice-test(\\|/)juice-test-behaviour(\\|/)).*', current_file)
	if match:
		return match.group(1)
	return None


class HighlightParamsCommand(sublime_plugin.EventListener):
	"""Highligts actual parameters in steps"""

	def on_modified(self, view):
		pass


class StopAutomationCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		global AUTOMATION_RUN
		if AUTOMATION_RUN is not None:
			AUTOMATION_RUN.kill()


class RunStoryCommand(sublime_plugin.TextCommand):

	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)
		self.current_file = None

	def run(self, edit, environment, instance):
		self.current_file = self.view.file_name()
		match = re.search(r'(\\|/)(\w+)\.story', self.current_file)
		story = DEFAULT_CONFIG[STORY_FILTER]
		folder = DEFAULT_CONFIG[STORY_FOLDER]
		if match:
			story = match.group(2)
			match = re.search(r'stories(\\|/)(.*)(\\|/)' + story + r'\.story', self.current_file)
			if match:
				folder = re.sub(r'\\', r'/', match.group(2))
		config = dict(DEFAULT_CONFIG)
		config[STORY_FOLDER] = folder
		config[STORY_FILTER] = story
		if environment == XDEVTINY:
			if instance == 10:
				config[TEST_URI] = DEFAULT_URLS[XDEVTINY].format(instance) + ":" + str(TINY10_PORT)
			else:
				config[TEST_URI] = DEFAULT_URLS[XDEVTINY].format(instance)
		else:
			config[TEST_URI] = DEFAULT_URLS[environment]
		args = ""
		for key in config.keys():
			if config[key] != "":
				args += "-D" + key + "=" + config[key] + " "
		if config[STORY_FILTER] != "" and config[STORY_FOLDER] != "":
			self.view.window().show_input_panel("Run", args[0:-1], self.get_input, None, None)

	def get_input(self, text):
		args = r'{0}{1}mvn -s {2} clean install -Dtest.contextView=false {3}'.format(MAVEN_FOLDER, os.sep, MAVEN_SETTINGS, text)
		print(args)
		global AUTOMATION_RUN
		AUTOMATION_RUN = Popen(args, stdout=PIPE, universal_newlines=True, cwd=get_automation_folder(self.current_file), shell=True)
		t = threading.Thread(target=self.read_output)
		t.setDaemon(True)
		t.start()

	def read_output(self):
		global AUTOMATION_RUN
		while AUTOMATION_RUN is not None and not AUTOMATION_RUN.poll():
			line = re.sub(r'(\n|\r)$', r'', AUTOMATION_RUN.stdout.readline())
			if line != "":
				print(line)		
		print("Automation was stopped")

class OpenJiraIssue(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		cursor = view.sel()
		line = view.substr(view.word(view.sel()[0].begin()))
		match = re.search(r'((thx|ofmr)(\d+))', line, re.IGNORECASE)
		if match is not None and len(match.groups()) > 2:
			issue = match.group(2).upper() + "-" + match.group(3)
			view.set_status("issue", issue)
			webbrowser.open_new_tab(JIRA_BROWSE + issue)
		else:
			view.set_status("issue", "Cannot parse issue number")


class OpenJavaFileCommand(sublime_plugin.TextCommand):
	"""Opens Java file"""

	def __init__(self, edit):
		sublime_plugin.TextCommand.__init__(self, edit)
		self.java_view = None
		self.found_step = None

	def run(self, edit):
		view = self.view
		step = view.substr(view.line(view.sel()[0].begin()))
		current_file = self.view.file_name()
		steps_path = get_automation_folder(current_file) + os.sep + STEPS_FOLDER
		java_file, found_step = self.find_file(steps_path, step)
		self.found_step = found_step
		print(java_file, found_step)
		if java_file is not None:
			window = self.view.window()
			self.java_view = window.open_file(java_file)
			t = threading.Thread(target=self.scroll_view)
			t.setDaemon(True)
			t.start()

	def scroll_view(self):
		while self.java_view.is_loading():
			time.sleep(0.01)		
		region = self.java_view.find(re.sub(r'\$', r'\\$', self.found_step), 0)
		self.java_view.show_at_center(region)
		self.java_view.sel().add(region)

	def find_file(self, steps_dir, step):
		step = str(re.sub("(Given|When|Then|And)\s", "", step))
		files = os.listdir(steps_dir)
		for source_file in files:
			full_path = os.path.join(steps_dir, source_file)
			if os.path.isdir(full_path):
				found_file, found_step = self.find_file(full_path, step)
				if found_file is not None:
					return found_file, found_step
			else:
				if not source_file.endswith(".java"):
					continue
				with open(full_path, "r") as source:
					for line in source.readlines():
						match = re.search(r'^\s*@(When|Then|Given|Alias|Aliases)\((.*)\)\s?$', line)
						if match is not None:
							if match.group(1) == "Aliases":
								aliases = re.findall(r'\s?"(.*)"\s?', line)
								for alias in aliases[0].split(r'", "'):
									if does_story_step_match_actual(step, alias):
										return full_path, alias
							else:
								candidate = match.group(2)[1:-1]	# annotation value without quotes
								if does_story_step_match_actual(step, candidate):
									return full_path, candidate
		return None, None


class AutoCompleteCollector(sublime_plugin.EventListener):	
	""" Autocompletes steps """
	files_list = None
	all_steps_list = None
	all_steps_parsed_list = None

	def __init__(self):
		self.files_list = []
		self.all_steps_list = []
		self.all_steps_parsed_list = []

	def get_java_steps_files(self, dir_name):
		""" Get all the java steps files """
		for root, dirnames, filenames in os.walk(dir_name):
			for filename in fnmatch.filter(filenames, "*Steps.java"):
				self.files_list.append(os.path.join(root, filename))
		return self.files_list

	def get_all_steps(self):
		""" Returns a list of @When('I click on button $button') lines' """
		if len(self.files_list) == 0:
			self.get_java_steps_files(STEPS_FOLDER)
		for file in self.files_list:
			with open(file) as java_step_class:
				for line in java_step_class:
					if re.match(r'\s*@(When|Then|Given)', line):
						self.all_steps_list.append(line.strip())

	def remove_characters_from_java_step(self, java_step):				
		return java_step.replace('@', '').replace('\"', '').replace('(', ' ').replace(')', ' ')

	def remove_characters_from_java_steps(self):
		""" Returns a list of When I click on button $button lines' """
		for step in self.all_steps_list:
			self.all_steps_parsed_list.append(self.remove_characters_from_java_step(step))

	def get_autocomplete_list(self, prefix):
		autocomplete_list = []		
		for step in self.all_steps_parsed_list:			
			if step.startswith(prefix):
				autocomplete_list.append(step)
		return autocomplete_list

	def on_post_save(self, view):		
		self.get_all_steps()		
		self.remove_characters_from_java_steps()								

	def on_query_completions(self, view, prefix, location):
		completions = []				
		print("files_list:" + str(len(self.files_list)))
		print("all_steps_list: " + str(len(self.all_steps_list)))
		print("all_steps_parsed_list: " + str(len(self.all_steps_parsed_list)))
		if '.story' in view.file_name():			
			print("prefix:" + prefix)
			print("len:" + str(len(self.get_autocomplete_list(prefix))))				
			return self.get_autocomplete_list(prefix)			
		completions.sort()				
		return (completions, sublime.INHIBIT_EXPLICIT_COMPLETIONS)	
