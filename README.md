# Doubt

A Python package that provides seamless Discord webhook integration for logging and progress tracking.

## Features

- Easy-to-use decorator for Discord logging
- Real-time progress tracking with progress bars
- Automatic message batching and flushing
- Asynchronous message sending
- Customizable logging levels and formats

## Installation

```bash
pip install git+https://github.com/nroggendorff/doubt.git
```

## Features in Detail

### Progress Tracking

The package automatically captures and displays progress bars from `tqdm` in Discord, showing:

- Progress percentage
- Visual progress bar
- Current/total items
- Estimated time remaining

### Message Batching

Messages are automatically batched and sent to Discord:

- When the buffer reaches 10 messages
- When a warning or error occurs
- When the flush interval is reached

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
