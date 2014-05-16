import sublime, sublime_plugin
import os
import re
import webbrowser

STEPS_FOLDER = r'C:\th\thx\repo\juice-test\juice-test-behaviour\src\main\java\com\thunderhead\juice\integration\jbehave\steps'


def does_story_step_match_actual(story_step, actual_step):
	step_pattern = get_step_pattern(actual_step)
	return story_step == actual_step or re.match(step_pattern, story_step) is not None


def get_step_pattern(step):
	params = re.findall(r'\s?(\$\w+|<\w+>)\s?', step)
	step_pattern = str(step)
	for param in params:
		step_pattern = re.sub(re.escape(param), '(.*)', step_pattern, 1)
	return step_pattern


class HighlightParamsCommand(sublime_plugin.EventListener):
	"""Highligts actual parameters in steps"""

	def on_modified(self, view):
		pass


class OpenJiraIssue(sublime_plugin.TextCommand):

	def run(self, edit):
		view = self.view
		cursor = view.sel()
		line = view.substr(view.word(view.sel()[0].begin()))
		match = re.search(r'((thx|ofmr)(\d+))', line, re.IGNORECASE)
		if match is not None and len(match.groups()) > 2:
			issue = match.group(2).upper() + "-" + match.group(3)
			print(issue)
			webbrowser.open_new_tab("https://thunderhead.jira.com/browse/" + issue)
		else:
			# print("Cannot parse issue number")
			view.set_status("issue", "Cannot parse issue number")


class OpenJavaFileCommand(sublime_plugin.TextCommand):
	"""Opens Java file"""

	def run(self, edit):
		view = self.view
		step = view.substr(view.line(view.sel()[0].begin()))
		java_file, found_step = self.find_file(STEPS_FOLDER, step)
		print(java_file, found_step)
		if java_file is not None:
			window = self.view.window()
			window.open_file(java_file)
			# add selection of found step in new tab

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
						match = re.search(r'^\s*@(When|Then|Given|Alias)\("(.*)"\)\s?$', line)
						if match is not None:
							candidate = match.group(2)
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
