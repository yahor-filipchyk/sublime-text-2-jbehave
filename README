JBehave Story Syntax - Sublime Text & TextMate plugin
=====================================================

A plugin for [Sublime Text 2][st2] and [TextMate][tm].

[JBehave][jb] is a [Behaviour Driven Development][bdd] framework
for the Java platform that allows business persons to write an
automatable description of the behaviour of an application 
or system:

> The language and its grammar represents the shared understanding of 
> the behaviour between the business users and the development team. And 
> as any language it evolves with the evolution of this shared 
> understanding. BDD provides the grammar, but the language is agreed 
> between the business and the team.


The [JBehave grammar][grmr] is defined in [EBNF][ebnf] at their 
website.

This plugin colors the story text allows visual identification of
subtle errors such as failing to capitalize the 'and' keyword
used to start a new step in the story.

To-Do:

 * GivenStories


Known Issue
-----------

This pattern could be improved:

  {	name = 'entity.section';  
    match = '^(Narrative|Scenario)\b';
  }

Ideally it should only match keywords with a trailing colon, but these patterns do not match:

  {	name = 'entity.section';
    match = '^(Narrative|Scenario)\:\b';
  }

  {	name = 'entity.section';
    match = '^(Narrative|Scenario)[\:]\b';
  }

  {	name = 'entity.section';
    match = '^(Narrative|Scenario)[\x3A]\b';
  }

The last example should match the colon according to [MacroMates regular expressions][re] but we get this error:

  invalid regular expression for 'match'-key 
  (too short multibyte code string for pattern 
  ^(Narrative|Scenario)\x3A\b)




[jb]: http://jbehave.org/reference/stable/
[bdd]: http://behaviour-driven.org/
[re]: http://manual.macromates.com/en/regular_expressions
[grmr]: http://jbehave.org/reference/stable/grammar.html
[st2]: http://www.sublimetext.com/2
[tm]: http://macromates.com
[ebnf]: http://en.wikipedia.org/wiki/Extended_Backus–Naur_Form

