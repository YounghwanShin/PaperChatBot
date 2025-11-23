'use client';

import React, { useState } from 'react';
import { Upload, FileText, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { FILE_UPLOAD } from '@/lib/constants';

interface PaperUploadProps {
  onUploadSuccess: (paper: { paper_id: string; title: string }) => void;
}

export default function PaperUpload({ onUploadSuccess }: PaperUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [abstract, setAbstract] = useState('');
  const [authors, setAuthors] = useState('');
  const [year, setYear] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      if (selectedFile.size > FILE_UPLOAD.MAX_SIZE) {
        setErrorMessage(`File size must be less than ${FILE_UPLOAD.MAX_SIZE / 1024 / 1024}MB`);
        setUploadStatus('error');
        return;
      }

      if (!selectedFile.name.endsWith('.pdf')) {
        setErrorMessage('Only PDF files are allowed');
        setUploadStatus('error');
        return;
      }

      setFile(selectedFile);
      setUploadStatus('idle');
      setErrorMessage('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file || !title.trim() || !abstract.trim()) {
      setErrorMessage('Please fill in all required fields and select a PDF file');
      setUploadStatus('error');
      return;
    }

    try {
      setIsUploading(true);
      setUploadStatus('idle');
      setErrorMessage('');

      const response = await apiClient.uploadPaper(
        file,
        title,
        abstract,
        authors,
        year ? parseInt(year) : undefined
      );

      setUploadStatus('success');
      setTimeout(() => {
        onUploadSuccess(response);
        resetForm();
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      setErrorMessage('Failed to upload paper. Please try again.');
      setUploadStatus('error');
    } finally {
      setIsUploading(false);
    }
  };

  const resetForm = () => {
    setFile(null);
    setTitle('');
    setAbstract('');
    setAuthors('');
    setYear('');
    setUploadStatus('idle');
    setErrorMessage('');
  };

  return (
    <div className="h-full p-6 overflow-y-auto">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white/90 backdrop-blur border border-gray-200 rounded-2xl p-8 shadow-lg">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
            <Upload className="w-7 h-7 text-blue-500" />
            Upload Research Paper
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDF File *
              </label>
              <div className="flex items-center gap-4">
                <label className="flex-1 cursor-pointer">
                  <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 hover:border-blue-400 transition-all">
                    <div className="flex flex-col items-center gap-2">
                      <FileText className="w-8 h-8 text-gray-400" />
                      <p className="text-sm text-gray-600">
                        {file ? file.name : 'Click to select PDF file'}
                      </p>
                      {file && (
                        <p className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      )}
                    </div>
                  </div>
                  <input
                    type="file"
                    accept={FILE_UPLOAD.ACCEPTED_TYPES}
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
              </div>
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Paper Title *
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter paper title"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all"
                required
              />
            </div>

            {/* Authors */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Authors
              </label>
              <input
                type="text"
                value={authors}
                onChange={(e) => setAuthors(e.target.value)}
                placeholder="e.g., John Doe, Jane Smith"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all"
              />
            </div>

            {/* Year */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Publication Year
              </label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                placeholder="e.g., 2024"
                min="1900"
                max={new Date().getFullYear()}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all"
              />
            </div>

            {/* Abstract */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Abstract *
              </label>
              <textarea
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="Enter paper abstract..."
                rows={6}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-blue-400 focus:ring-4 focus:ring-blue-100 transition-all resize-none"
                required
              />
            </div>

            {/* Status Messages */}
            {uploadStatus === 'success' && (
              <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                <CheckCircle className="w-5 h-5" />
                <span>Paper uploaded successfully!</span>
              </div>
            )}

            {uploadStatus === 'error' && errorMessage && (
              <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                <XCircle className="w-5 h-5" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* Submit Button */}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={isUploading || !file || !title.trim() || !abstract.trim()}
                className="flex-1 px-6 py-4 bg-gradient-to-br from-blue-500 to-indigo-600 text-white rounded-2xl hover:shadow-lg hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200 flex items-center justify-center gap-2 font-medium shadow-md"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Uploading & Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    Upload Paper
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={resetForm}
                disabled={isUploading}
                className="px-6 py-4 bg-gray-100 text-gray-700 rounded-2xl hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
              >
                Reset
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
