import React, { useState, useEffect } from 'react';

interface FileInfo {
  filename: string;
  size: number;
  processed: boolean;
  date_modified: number;
}

interface UploadResponse {
  filename?: string;
  file_type: string;
  status: string;
  url?: string;
  error?: string;
}

// Add props interface
interface FileUploadProps {
  onUpload?: (result: any) => void;
}

// Update component signature
const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState<string>('');
  const [uploadMode, setUploadMode] = useState<'file' | 'youtube'>('file');
  const [fileType, setFileType] = useState<string>('document');
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [files, setFiles] = useState<FileInfo[]>([]);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      const response = await fetch('http://localhost:8000/files/');
      const data = await response.json();
      setFiles(data.files || []);
    } catch (error) {
      console.error('Error fetching files:', error);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleYoutubeUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setYoutubeUrl(event.target.value);
  };

  const handleFileTypeChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setFileType(event.target.value);
  };

  // In the handleUpload function, add calls to onUpload:
  const handleUpload = async () => {
    if (uploadMode === 'file' && !selectedFile) {
      setUploadStatus('Please select a file first.');
      return;
    }
    
    if (uploadMode === 'youtube' && !youtubeUrl.trim()) {
      setUploadStatus('Please enter a YouTube URL.');
      return;
    }

    setUploadStatus('Uploading...');

    try {
      const formData = new FormData();
      
      if (uploadMode === 'file') {
        formData.append('file', selectedFile!);
        formData.append('file_type', fileType);
        
        const response = await fetch('http://localhost:8000/upload/', {
          method: 'POST',
          body: formData,
        });
        
        const result: UploadResponse = await response.json();
        
        if (response.ok) {
          setUploadStatus(`File uploaded successfully: ${result.filename}`);
          setSelectedFile(null);
          fetchFiles();
          // Add this line
          onUpload?.(result);
        } else {
          setUploadStatus(`Upload failed: ${result.error || 'Unknown error'}`);
        }
      } else {
        // YouTube upload
        formData.append('url', youtubeUrl);
        formData.append('file_type', 'video');
        
        const response = await fetch('http://localhost:8000/upload-youtube/', {
          method: 'POST',
          body: formData,
        });
        
        const result: UploadResponse = await response.json();
        
        if (response.ok) {
          setUploadStatus(`YouTube video processing started: ${result.url}`);
          setYoutubeUrl('');
          fetchFiles();
          // Add this line
          onUpload?.(result);
        } else {
          setUploadStatus(`Upload failed: ${result.error || 'Unknown error'}`);
        }
      }
    } catch (error) {
      setUploadStatus(`Upload failed: ${error}`);
    }
  };

  return (
    <div className="file-upload">
      <h2>Upload Content</h2>
      
      {/* Upload Mode Toggle */}
      <div className="upload-mode-toggle" style={{ marginBottom: '20px' }}>
        <label style={{ marginRight: '20px' }}>
          <input
            type="radio"
            value="file"
            checked={uploadMode === 'file'}
            onChange={(e) => setUploadMode(e.target.value as 'file' | 'youtube')}
            style={{ marginRight: '5px' }}
          />
          Upload File
        </label>
        <label>
          <input
            type="radio"
            value="youtube"
            checked={uploadMode === 'youtube'}
            onChange={(e) => setUploadMode(e.target.value as 'file' | 'youtube')}
            style={{ marginRight: '5px' }}
          />
          YouTube URL
        </label>
      </div>

      {uploadMode === 'file' ? (
        <div className="file-upload-section">
          <input type="file" onChange={handleFileChange} style={{ marginBottom: '10px' }} />
          <select value={fileType} onChange={handleFileTypeChange} style={{ marginLeft: '10px' }}>
            <option value="document">Document</option>
            <option value="image">Image</option>
            <option value="video">Video</option>
            <option value="audio">Audio</option>
          </select>
        </div>
      ) : (
        <div className="youtube-upload-section">
          <input
            type="url"
            placeholder="Enter YouTube URL (e.g., https://www.youtube.com/watch?v=...)"
            value={youtubeUrl}
            onChange={handleYoutubeUrlChange}
            style={{ width: '100%', marginBottom: '10px', padding: '8px' }}
          />
        </div>
      )}

      <button 
        onClick={handleUpload} 
        disabled={uploadMode === 'file' ? !selectedFile : !youtubeUrl.trim()}
        style={{ 
          padding: '10px 20px', 
          backgroundColor: '#007bff', 
          color: 'white', 
          border: 'none', 
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        {uploadMode === 'file' ? 'Upload File' : 'Process YouTube Video'}
      </button>

      {uploadStatus && <p className="upload-status" style={{ marginTop: '10px' }}>{uploadStatus}</p>}

      {/* Display uploaded files */}
      <div className="uploaded-files" style={{ marginTop: '30px' }}>
        <h3>Uploaded Resources</h3>
        {files.length === 0 ? (
          <p>No files uploaded yet.</p>
        ) : (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {files.map((file, index) => (
              <li key={index} style={{ 
                padding: '10px', 
                margin: '5px 0', 
                backgroundColor: file.processed ? '#d4edda' : '#fff3cd',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}>
                <span className="filename" style={{ fontWeight: 'bold' }}>{file.filename}</span>
                <span className="file-size" style={{ marginLeft: '10px', color: '#666' }}>({(file.size / 1024).toFixed(1)} KB)</span>
                <span className="status" style={{ float: 'right' }}>
                  {file.processed ? '✅ Processed' : '⏳ Processing...'}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
