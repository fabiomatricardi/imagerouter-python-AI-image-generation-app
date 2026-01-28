# ImageRouter.io GUI Generator

**Transform your ImageRouter.io API key into a professional desktop app.** No CLI complexity—just point, click, generate, and download stunning AI images from 50+ free models.

[
[
[
[

## ✨ Features

| Feature | ✅ Implemented |
| :-- | :-- |
| **Model Selection** | 8+ free ImageRouter models (FLUX, SDXL-Turbo, etc.) |
| **Custom Dimensions** | 512-1024px (64px steps): portrait, landscape, square |
| **API Key Manager** | Secure `config.json` storage + Settings tab |
| **Live Preview** | Generated PNG displays instantly in-app |
| **Auto-Save** | Timestamp + random ID filenames |
| **Standalone EXE** | PyInstaller onefile bundle (~150MB) |
| **Threaded API** | No freezing during generation |
| **Cross-Platform** | Windows 11, Ubuntu, Alpine Linux |

## 🎮 Quick Start

### 1. Install Dependencies

```bash
pip install PySide6 requests pillow pyinstaller
```


### 2. Get Free API Key

1. [Sign up at imagerouter.io](https://imagerouter.io)
2. Dashboard → API Keys → Create Key (FREE tier: 50 images/day)
3. Copy your key
4. Top up at least 5$: free models will not charge any costs, but it is required to have a minimum there

### 3. Run App

```bash
python image_gen_gui.py
```

- **First run**: Settings tab → paste API key → Save
- **Generate**: Pick model, enter prompt, adjust size → Click Generate
- **Done**: Preview appears + PNG auto-saves + opens in viewer


### 4. Create Standalone EXE (Windows)

```bash
pyinstaller image_gen_gui.spec
```

→ `dist/ImageGen.exe` (works anywhere, no Python needed)

## 📱 Screenshots

| Generate Tab | Settings Tab | Preview |
| :-- | :-- | :-- |
|  |  |  |

## 🏗️ Architecture Deep Dive

### Core Components

```python
class ImageGenApp(QMainWindow):          # Main window + tabs
    ├── load_config()                   # JSON API key management
    ├── create_main_tab()               # Prompt + model + size controls
    └── create_settings_tab()           # Secure API key input

class ApiWorker(QThread):                # Non-blocking API calls
    ├── image_generated (Signal)        # Success: filename + preview
    ├── error_occurred (Signal)         # API errors → QMessageBox
    └── run()                           # requests.post → PIL → save
```


### Key Implementation Details

#### 1. **Dimension Constraints**

```python
self.width_spin = QSpinBox()
self.width_spin.setRange(512, 1024)    # AI model limits
self.width_spin.setSingleStep(64)      # Pixel alignment
self.width_spin.setValue(1024)         # Landscape default
```


#### 2. **Threaded Generation (No UI Freeze)**

```python
self.worker = ApiWorker(api_key, prompt, model, f"{w}x{h}")
self.worker.image_generated.connect(self.on_image_generated)
self.worker.start()                    # Background thread
```


#### 3. **Secure Config Management**

```python
def load_config(self):
    if os.path.exists('config.json'):
        with open('config.json') as f:
            self.api_key = json.load(f).get('api_key', '')
    else:
        self.save_config()  # Creates empty config.json

def save_config(self):
    json.dump({'api_key': self.api_key}, open('config.json', 'w'), indent=2)
```


#### 4. **Image Pipeline**

```
API Response (URL) → requests.get() → PIL.Image → PNG save → QPixmap preview → img.show()
```


### Filename Format

```
image_1704061234_ab12cd.png  # timestamp + 6-char random
```


## 🔧 PyInstaller Bundle

### SPEC File Breakdown

```spec
Analysis([...])                    # Scans imports (PySide6, PIL, requests)
hiddenimports=['PySide6.QtSvg']    # Qt image formats
EXE(..., console=False)            # Windowed app, no terminal
```

**Build**: `pyinstaller image_gen_gui.spec`
**Output**: `dist/ImageGen.exe` (~150MB, fully standalone)

**Pro Tip**: Add `--icon=icon.ico` for branded executable.

## 🚀 Development Roadmap

- [x] Core GUI + API integration
- [x] Config.json persistence
- [x] Model dropdown + size constraints
- [x] Threading + progress bar
- [x] PyInstaller onefile
- [ ] Dynamic model list (API fetch)
- [ ] Batch generation
- [ ] Prompt history
- [ ] Dark mode toggle


## 📚 Usage Examples

```
Prompt: "futuristic cyberpunk city at night, neon lights, flying cars"
Model: black-forest-labs/FLUX-2-klein-4b:free
Size: 1024x640 (landscape)
→ Generates: image_1704061234_xy789z.png
```


## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - Free for personal/commercial use. See [LICENSE](LICENSE).

## 🙏 Acknowledgments

- [ImageRouter.io](https://imagerouter.io) - Free AI image API
- [PySide6](https://www.pyside.org) - Professional Qt bindings
- [PyInstaller](https://pyinstaller.org) - Standalone packaging
- Your CLI code → GUI transformation! 🎉

***

**⭐ Star if useful! Created with Python + PySide6 + ❤️**

*Made by [thePoorGPUguy] for Python GUI enthusiasts*

***




