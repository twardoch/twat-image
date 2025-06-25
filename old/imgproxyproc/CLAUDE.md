# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the `imgproxyproc` project - a tool for processing high-resolution images through low-resolution models while preserving quality. The tool uses a delta-based approach to maintain image fidelity when working with resolution-limited models.

## Architecture

The core concept involves:
1. **Downsampling**: Converting high-res images to low-res for model processing
2. **Delta Calculation**: Computing the difference between model input and output as delta images
3. **Upscaling**: Bringing deltas back to original resolution using various methods
4. **Merging**: Applying upscaled deltas to the original high-res image

# When you write code

- Iterate gradually, avoiding major changes 
- Minimize confirmations and checks
- Preserve existing code/structure unless necessary
- Use constants over magic numbers
- Check for existing solutions in the codebase before starting
- Check often the coherence of the code you’re writing with the rest of the code. 
- Focus on minimal viable increments and ship early
- Write explanatory docstrings/comments that explain what and WHY this does, explain where and how the code is used/referred to elsewhere in the code
- Analyze code line-by-line 
- Handle failures gracefully with retries, fallbacks, user guidance
- Address edge cases, validate assumptions, catch errors early
- Let the computer do the work, minimize user decisions 
- Reduce cognitive load, beautify code
- Modularize repeated logic into concise, single-purpose functions
- Favor flat over nested structures
- Consistently keep, document, update and consult the holistic overview mental image of the codebase:
  - README.md (purpose and functionality) 
  - CHANGELOG.md (past changes)
  - TODO.md (future goals)
  - PROGRESS.md (detailed flat task list)

## Use MCP tools if you can

Before you start writing: 

- consult the `context7` tool for most up-to-date software package documentation
- use `sequentialthinking` from the `sequential-thinking` tool to think about the best way to solve the task; 
- use `search` and `fetch_content` from the `search_web_ddg` tool to get more info on the web; 

As you keep working: 

- consult with the `openai/o3` model via `chat_completion` from the `ask-chatgpt` tool to get help with the task;

## Keep track of paths

In each source file, maintain the up-to-date `this_file` record that shows the path of the current file relative to project root. Place the `this_file` record near the top of the file, as a comment after the shebangs, or in the YAML Markdown frontmatter. 

## When you write Python

- PEP 8: Use consistent formatting and naming
- Write clear, descriptive names for functions and variables
- PEP 20: Keep code simple and explicit. Prioritize readability over cleverness
- Use type hints in their simplest form (list, dict, | for unions)
- PEP 257: Write clear, imperative docstrings
- Use f-strings. Use structural pattern matching where appropriate
- ALWAYS add "verbose" mode logugu-based logging, & debug-log
- For CLI Python scripts, use fire & rich, and start the script with 

```
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["PKG1", "PKG2"]
# ///
# this_file: PATH_TO_CURRENT_FILE
```

Ask before extending/refactoring existing code in a way that may add complexity or break things. 

When you’re finished, print "Wait, but" to go back, think & reflect, revise & improvement what you’ve done (but don’t invent functionality freely). Repeat this. But stick to the goal of "minimal viable next version". Lead two experts: "Ideot" for creative, unorthodox ideas, and "Critin" to critique flawed thinking and moderate for balanced discussions. The three of you shall illuminate knowledge with concise, beautiful responses, process methodically for clear answers, collaborate step-by-step, sharing thoughts and adapting. If errors are found, step back and focus on accuracy and progress.

## After Python changes run:

```
fd -e py -x autoflake {}; fd -e py -x pyupgrade --py312-plus {}; fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {}; fd -e py -x ruff format --respect-gitignore --target-version py312 {}; python -m pytest;
```

Be creative, diligent, critical, relentless & funny!

## Implementation Guidelines

1. The tool should implement two main operations via Fire CLI:
   - `split`: Downsample high-res images and prepare for model processing
   - `merge`: Apply delta images back to original high-res images

2. Use the parent directory's CLAUDE.md guidelines for general coding practices

3. Focus on handling edge cases gracefully:
   - Different image aspect ratios requiring padding
   - Precision preservation through optional refined delta images
   - Various upscaling methods (basic and command-based)

## Key Technical Considerations

- Delta images use mid-gray (RGB 127,127,127) to represent no change
- Support both single delta and dual delta (main + refined) workflows
- Ensure lossless formats for delta images to preserve precision
- Handle dimension mismatches between delta and input images properly