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

interface FileUploadProps {
  onUpload?: (result: any) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [youtubeUrl, setYoutubeUrl] = useState<string>('');
  const [uploadMode, setUploadMode] = useState<'file' | 'youtube'>('file');
  const [fileType, setFileType] = useState<string>('document');
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [showDone, setShowDone] = useState<boolean>(false);

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

  const handleDeleteFile = async (filename: string) => {
    if (!window.confirm(`Are you sure you want to delete "${filename}"?`)) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/files/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Refresh the file list after successful deletion
        fetchFiles();
      } else {
        const errorData = await response.json();
        alert(`Error deleting file: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error deleting file:', error);
      alert('Error deleting file. Please try again.');
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

  const handleUpload = async () => {
    if (uploadMode === 'file' && !selectedFile) {
      return;
    }
    
    if (uploadMode === 'youtube' && !youtubeUrl.trim()) {
      return;
    }

    setIsProcessing(true);
    setShowDone(false);

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
          setSelectedFile(null);
          onUpload?.(result);
        }
      } else {
        formData.append('url', youtubeUrl);
        formData.append('file_type', 'video');
        
        const response = await fetch('http://localhost:8000/upload-youtube/', {
          method: 'POST',
          body: formData,
        });
        
        const result: UploadResponse = await response.json();
        
        if (response.ok) {
          setYoutubeUrl('');
          onUpload?.(result);
        }
      }
      
      // Show done state
      setShowDone(true);
      
      // Hide processing screen and refresh files after delay
      setTimeout(() => {
        setIsProcessing(false);
        setShowDone(false);
        fetchFiles();
      }, 2000);
      
    } catch (error) {
      setIsProcessing(false);
      setShowDone(false);
    }
  };

  // Simple Processing Screen
  const ProcessingScreen = () => (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '16px',
        textAlign: 'center',
        minWidth: '300px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
      }}>
        {showDone ? (
          <>
            <div style={{
              width: '60px',
              height: '60px',
              backgroundColor: '#28a745',
              borderRadius: '50%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              margin: '0 auto 20px',
              fontSize: '30px',
              color: 'white'
            }}>✓</div>
            <h3 style={{ margin: '0', color: '#28a745', fontSize: '24px' }}>Done!</h3>
          </>
        ) : (
          <>
            <div style={{
              width: '60px',
              height: '60px',
              border: '4px solid #007bff',
              borderTop: '4px solid transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 20px'
            }}></div>
            <h3 style={{ margin: '0', color: '#007bff', fontSize: '24px' }}>Processing...</h3>
          </>
        )}
      </div>
    </div>
  );

  return (
    <>
      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      
      {/* Processing Screen */}
      {isProcessing && <ProcessingScreen />}
      
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
              disabled={isProcessing}
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
              disabled={isProcessing}
            />
            YouTube URL
          </label>
        </div>

        {/* File Type Selection */}
        <div className="file-type-selection" style={{ marginBottom: '20px' }}>
          <label htmlFor="file-type">Content Type: </label>
          <select 
            id="file-type" 
            value={fileType} 
            onChange={handleFileTypeChange}
            disabled={isProcessing}
            style={{ marginLeft: '10px', padding: '5px' }}
          >
            <option value="document">Document</option>
            <option value="image">Image</option>
            <option value="data">Data/Spreadsheet</option>
            <option value="video">Video</option>
          </select>
        </div>

        {/* Upload Controls */}
        {uploadMode === 'file' ? (
          <div className="file-upload-section">
            <input 
              type="file" 
              onChange={handleFileChange}
              disabled={isProcessing}
              style={{ marginBottom: '10px' }}
            />
            <button 
              onClick={handleUpload}
              disabled={!selectedFile || isProcessing}
              style={{
                padding: '10px 20px',
                backgroundColor: (!selectedFile || isProcessing) ? '#ccc' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: (!selectedFile || isProcessing) ? 'not-allowed' : 'pointer'
              }}
            >
              Upload File
            </button>
          </div>
        ) : (
          <div className="youtube-upload-section">
            <input
              type="url"
              placeholder="Enter YouTube URL"
              value={youtubeUrl}
              onChange={handleYoutubeUrlChange}
              disabled={isProcessing}
              style={{ 
                width: '300px', 
                padding: '8px', 
                marginRight: '10px',
                marginBottom: '10px'
              }}
            />
            <button 
              onClick={handleUpload}
              disabled={!youtubeUrl.trim() || isProcessing}
              style={{
                padding: '10px 20px',
                backgroundColor: (!youtubeUrl.trim() || isProcessing) ? '#ccc' : '#007bff',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: (!youtubeUrl.trim() || isProcessing) ? 'not-allowed' : 'pointer'
              }}
            >
              Process YouTube Video
            </button>
          </div>
        )}

        {/* Files List */}
        <div className="files-list" style={{ marginTop: '30px' }}>          <h3>Uploaded Files</h3>
          {files.length === 0 ? (
            <p>No files uploaded yet.</p>
          ) : (
            <div className="files-grid">
              {files.map((file, index) => (
                <div key={index} className="file-item" style={{
                  border: '1px solid #ddd',
                  padding: '15px',
                  margin: '10px 0',
                  borderRadius: '8px',
                  backgroundColor: file.processed ? '#f8f9fa' : '#fff3cd'
                }}>
                  <div className="file-info">
                    <h4 style={{ margin: '0 0 10px 0' }}>{file.filename}</h4>
                    <p style={{ margin: '5px 0', color: '#666' }}>Size: {(file.size / 1024).toFixed(2)} KB</p>
                    <p style={{ margin: '5px 0', color: '#666' }}>
                      Modified: {new Date(file.date_modified * 1000).toLocaleDateString()}
                    </p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
                      <div className="status-indicator" style={{
                        display: 'inline-block',
                        padding: '4px 8px',
                        borderRadius: '12px',
                        fontSize: '12px',
                        fontWeight: 'bold',
                        backgroundColor: file.processed ? '#28a745' : '#ffc107',
                        color: 'white'
                      }}>
                        {file.processed ? '✓ Processed' : '⏳ Processing'}
                      </div>
                      <button
                        onClick={() => handleDeleteFile(file.filename)}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px',
                          fontWeight: 'bold'
                        }}
                        onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#c82333'}
                        onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#dc3545'}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default FileUpload;
