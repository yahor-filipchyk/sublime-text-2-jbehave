import sublime, sublime_plugin
import os
import re

STEPS_FOLDER = r'C:\th\thx\repo\juice-test\juice-test-behaviour\src\main\java\com\thunderhead\juice\integration\jbehave\steps'

class HighlightParamsCommand(sublime_plugin.EventListener):
	"""Highligts actual parameters in steps"""

	def highlightSteps(self):
		print("Text modified")
		pass

	def on_modified(self, view):
		print(view.substr(view.visible_region()))

class OpenJavaFileCommand(sublime_plugin.TextCommand):
	"""Opens Java file"""

	def highlightSteps(self):
		print("Text modified")
		pass

	def run(self, edit):
		view = self.view
		step = view.substr(view.line(self.view.sel()[0].begin()))
		java_file = self.find_file(STEPS_FOLDER, step)
		print(java_file)
		if java_file is not None:
			self.view.window().open_file(java_file)
		# self.view.window().active_view()

	def find_file(self, steps_dir, step):
		step = str(re.sub("(Given|When|Then|And)\s", "", step))
		files = os.listdir(steps_dir)
		for source_file in files:
			full_path = os.path.join(steps_dir, source_file)
			if os.path.isdir(full_path):
				found = self.find_file(full_path, step)
				if found is not None:
					return found
			else:
				if not source_file.endswith(".java"):
					continue
				with open(full_path, "r") as source:
					for line in source.readlines():
						match = re.search(r'^\s*@(When|Then|Given)\("(.*)"\)\s?$', line)
						if match is not None:
							candidate = match.group(2)
							params = re.findall(r'\s?(\$\w+|<\w+>)\s?', candidate)
							step_pattern = str(candidate)
							for param in params:
								step_pattern = re.sub(re.escape(param), '(.*)', step_pattern, 1)
							if step == candidate or re.match(step_pattern, step) is not None:
								return full_path

class AutoCompleteStepCommand(sublime_plugin.TextCommand):
	"""Autocompletes steps"""

	def run(self, view):
		print("Going to autocomplete")
