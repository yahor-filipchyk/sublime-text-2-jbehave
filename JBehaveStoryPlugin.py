import sublime, sublime_plugin
import os
import re

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

class OpenJavaFileCommand(sublime_plugin.TextCommand):
	"""Opens Java file"""

	def run(self, edit):
		view = self.view
		step = view.substr(view.line(self.view.sel()[0].begin()))
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

class AutoCompleteStepCommand(sublime_plugin.TextCommand):
	"""Autocompletes steps"""

	def run(self, view):
		print("Going to autocomplete")
