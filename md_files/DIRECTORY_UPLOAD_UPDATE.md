# Directory Upload Feature Update

## Summary
Successfully updated the DocuSearch web interface to replace single/multiple document upload options with a directory selection feature that shows the selected directory path and file count.

## Changes Made

### 1. HTML Template Updates (`templates/index.html`)

#### Upload Section Changes:
- **Removed**: Single/Multiple document upload mode selection
- **Added**: Directory picker with `webkitdirectory` attribute
- **Added**: Selected directory path display
- **Added**: File count display showing supported vs total files

#### New Elements:
```html
<div class="directory-input-wrapper">
    <input type="file" id="directoryInput" class="directory-input" webkitdirectory directory multiple>
    <label for="directoryInput" class="directory-input-label">
        📁 Choose a directory to upload<br>
        <small>Select a folder to upload all supported documents (PDF, DOCX, TXT, HTML)</small>
    </label>
</div>

<div class="selected-directory" id="selectedDirectory" style="display: none;">
    <h4>Selected Directory:</h4>
    <div class="directory-path" id="directoryPath"></div>
    <div class="file-count" id="fileCount"></div>
</div>
```

### 2. CSS Styling Updates

#### New Styles Added:
- `.directory-input-wrapper` - Container for directory input
- `.directory-input` - Hidden file input for directory selection
- `.directory-input-label` - Styled label for directory picker
- `.selected-directory` - Container for showing selected directory info
- `.directory-path` - Monospace display for directory path
- `.file-count` - Display for file count information

#### Removed Styles:
- `.upload-mode-selection` - Old upload mode selection
- `.mode-options` - Radio button options
- `.radio-custom` - Custom radio button styling
- `.bulk-upload-info` - Old bulk upload info display

### 3. JavaScript Functionality Updates

#### Directory Selection Handler:
```javascript
document.getElementById('directoryInput').addEventListener('change', function(e) {
    const files = e.target.files;
    // Extract directory path from first file
    // Filter supported files (PDF, DOCX, TXT, HTML)
    // Display directory path and file count
});
```

#### Upload Logic Changes:
- **Removed**: Upload mode detection logic
- **Updated**: Always use bulk upload for directory uploads
- **Added**: File filtering to only process supported file types
- **Updated**: Error messages to reflect directory selection

### 4. User Experience Improvements

#### Directory Selection:
- Users can now select entire directories instead of individual files
- Directory path is displayed clearly when selected
- File count shows both supported and total files found
- Only supported file types (PDF, DOCX, TXT, HTML) are processed

#### Visual Feedback:
- Green-highlighted selected directory information
- Clear indication of how many files will be processed
- Monospace font for directory path display
- Responsive design maintained

## Technical Details

### File Type Filtering:
The system automatically filters files to only process supported types:
```javascript
const supportedFiles = Array.from(files).filter(file => {
    const extension = file.name.toLowerCase().split('.').pop();
    return ['pdf', 'docx', 'txt', 'html'].includes(extension);
});
```

### Directory Path Extraction:
Uses `webkitRelativePath` to extract the directory structure:
```javascript
const fullPath = firstFile.webkitRelativePath || firstFile.name;
const directoryPath = fullPath.substring(0, fullPath.lastIndexOf('/'));
```

### Error Handling:
- Validates that a directory is selected
- Ensures at least one supported file is found
- Provides clear error messages for unsupported directories

## Benefits

1. **Simplified Interface**: Single directory picker instead of multiple upload modes
2. **Better User Experience**: Clear visual feedback of selected directory and file count
3. **Efficient Processing**: Automatic filtering of supported file types
4. **Bulk Operations**: All files in directory processed with same metadata settings
5. **Path Visibility**: Users can see exactly which directory they selected

## Testing

The updated interface has been tested and verified to work correctly with:
- ✅ Directory selection functionality
- ✅ Directory path display
- ✅ File count display
- ✅ File type filtering
- ✅ Bulk upload processing
- ✅ GROBID integration
- ✅ Author array structure

## Usage

1. Click "📁 Choose a directory to upload"
2. Select a folder containing documents
3. View the selected directory path and file count
4. Select desired metadata fields to extract
5. Click "Upload & Parse Directory" to process all supported files

The system will automatically filter and process only PDF, DOCX, TXT, and HTML files from the selected directory.
