# Web Recorder

A Python package for recording, storing, and replaying web interactions using rrweb and Playwright.

## Overview

Web Recorder is a powerful tool that allows you to capture and replay web interactions. It combines the capabilities of rrweb for recording web sessions with Playwright for browser automation, making it perfect for:
- Recording web interactions for testing
- Creating web session replays
- Automating web workflows
- Debugging web applications

## Installation

```bash
pip install web-recorder
```

## Dependencies

- rrweb: For recording web sessions
- Playwright: For browser automation and replay
- Python 3.7+

## Usage

### Recording a Web Session

```python
from web_recorder import Recorder
# Initialize the recorder
recorder = Recorder()

# Start recording
recording = await recorder.record()

```

### Replaying a Recording

```python
# Replay a recording
recording.replay(recording)
```

### Exporting/Importing a Recording

```python

from web_recorder import Recording

# Export a recording
recording.export(
  path=events_path,
)

# Import a Recording
recording = Recording.from_file(events_path)
```

## Features

- High-fidelity web session recording
- Accurate replay of recorded sessions
- Support for all major web browsers
- Event-based recording system
- Easy-to-use API

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

Pranav Raja (pranavraja99@gmail.com)  
Yasir Nadeem (m-yasir.dev@protonmail.com)


