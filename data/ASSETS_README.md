# Android Assets

This directory contains Android packaging assets for the AI Chat Assistant.

## Current Assets

### icon.png (512x512)
- **Current**: Placeholder blue icon with "AI" text
- **Purpose**: Application launcher icon
- **Requirements**: Should be 512x512 PNG with transparency support
- **Recommendation**: Replace with your app's branded icon

### presplash.png (1080x1920)
- **Current**: Placeholder splash screen with "AI Chat Assistant" text
- **Purpose**: Loading screen shown while app initializes
- **Requirements**: Should be 1080x1920 PNG (standard Android resolution)
- **Recommendation**: Replace with your branded splash screen

## How to Replace

1. Create your custom images:
   - **icon.png**: 512x512 PNG (square, with transparency preferred)
   - **presplash.png**: 1080x1920 PNG (portrait orientation)

2. Replace the placeholder files in this directory:
   ```bash
   cp /path/to/your/icon.png data/icon.png
   cp /path/to/your/presplash.png data/presplash.png
   ```

3. Rebuild your Android APK with Buildozer:
   ```bash
   buildozer android debug
   ```

## Design Guidelines

### Icon Design
- Use simple, recognizable shapes
- Ensure good contrast on various backgrounds
- Consider adaptive icon requirements for Android 8.0+
- Test on both light and dark backgrounds

### Presplash Design
- Include app name/logo
- Keep it simple and clean
- Consider loading time (image should be optimized)
- Portrait orientation only (1080x1920)
- Ensure text is readable at full size

## Asset Creation Tools

Recommended tools for creating assets:
- **GIMP**: Free, open-source image editor
- **Inkscape**: Vector graphics editor
- **Photoshop**: Professional image editing
- **Canva**: Online design tool with templates
- **Figma**: Collaborative design tool

## Additional Adaptive Icons (Optional)

For Android 8.0+ support, you can also add:
- `icon_fg.png`: Foreground layer for adaptive icon (512x512)
- `icon_bg.png`: Background layer for adaptive icon (512x512)

These would be configured in buildozer.spec as:
```spec
icon.adaptive_foreground.filename = %(source.dir)s/data/icon_fg.png
icon.adaptive_background.filename = %(source.dir)s/data/icon_bg.png
```
