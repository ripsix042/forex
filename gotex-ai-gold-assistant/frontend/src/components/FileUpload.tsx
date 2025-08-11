import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface FileUploadProps {
  onUpload: (result: any) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUpload }) => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('');
  const [files, setFiles] = useState<string[]>([]);
  const [fileType, setFileType] = useState<string>('video');

  const fetchFiles = async () => {
    try {
      const response = await axios.get('http://localhost:8000/files/');
      setFiles(response.data.files);
    } catch (error) {
      setFiles([]);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);

    try {
      setStatus('Uploading...');
      const response = await axios.post('http://localhost:8000/upload/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setStatus(`Success: ${response.data.filename}`);
      setFile(null);
      fetchFiles();
      onUpload(response.data);
    } catch (error) {
      setStatus('Upload failed');
    }
  };

  return (
    <div className="p-5 border rounded shadow-md bg-white max-w-md mx-auto mt-8">
      <h2 className="text-lg font-bold mb-3">Upload Trading Resources</h2>
      <p className="text-sm text-gray-600 mb-3">Upload educational content about gold trading for analysis and reference.</p>
      
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Content Type</label>
        <select 
          value={fileType} 
          onChange={e => setFileType(e.target.value)} 
          className="w-full p-2 border rounded focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="video">Video</option>
          <option value="image">Chart/Image</option>
          <option value="pdf">PDF Document</option>
          <option value="csv">CSV Data</option>
          <option value="excel">Excel Spreadsheet</option>
        </select>
      </div>
      
      <div className="mb-3">
        <label className="block text-sm font-medium text-gray-700 mb-1">Select File</label>
        <input 
          type="file" 
          onChange={handleFileChange} 
          className="w-full p-2 border rounded text-sm" 
        />
      </div>
      
      <button
        onClick={handleUpload}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded disabled:opacity-50 transition duration-200"
        disabled={!file}
      >
        {file ? `Upload ${file.name}` : 'Select a file'}
      </button>
      
      {status && (
        <div className={`mt-3 text-sm p-2 rounded ${status.includes('Success') ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
          {status}
        </div>
      )}
      
      <div className="mt-5 border-t pt-3">
        <h3 className="font-semibold mb-2">Uploaded Resources:</h3>
        {files.length > 0 ? (
          <ul className="divide-y">
            {files.map((fname) => (
              <li key={fname} className="py-2 flex items-center">
                <span className="mr-2">
                  {fname.endsWith('.pdf') ? '📄' : 
                   fname.endsWith('.mp4') || fname.endsWith('.mov') ? '🎬' : 
                   fname.endsWith('.jpg') || fname.endsWith('.png') ? '🖼️' : 
                   fname.endsWith('.csv') ? '📊' : 
                   fname.endsWith('.xls') || fname.endsWith('.xlsx') ? '📑' : '📁'}
                </span>
                {fname}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-500 italic">No files uploaded yet</p>
        )}
      </div>
    </div>
  );
};

export default FileUpload;
