import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import DocumentManager from '../DocumentManager';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Create a mock store
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      documents: (state = initialState, action) => state
    }
  });
};

describe('DocumentManager', () => {
  const mockDocuments = [
    {
      id: 1,
      filename: 'test1.pdf',
      content: 'Test content 1',
      created_at: '2024-01-01T00:00:00Z'
    },
    {
      id: 2,
      filename: 'test2.pdf',
      content: 'Test content 2',
      created_at: '2024-01-02T00:00:00Z'
    }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders document manager correctly', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    expect(screen.getByText('Document Manager')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /upload document/i })).toBeInTheDocument();
    expect(screen.getByRole('list')).toBeInTheDocument();
  });

  it('displays list of documents', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: mockDocuments
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    await waitFor(() => {
      expect(screen.getByText('test1.pdf')).toBeInTheDocument();
      expect(screen.getByText('test2.pdf')).toBeInTheDocument();
    });
  });

  it('handles document upload', async () => {
    const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        id: 3,
        filename: 'test.pdf',
        content: 'test content',
        created_at: '2024-01-03T00:00:00Z'
      }
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    const fileInput = screen.getByLabelText(/upload document/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('test.pdf')).toBeInTheDocument();
      expect(mockedAxios.post).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(FormData),
        expect.any(Object)
      );
    });
  });

  it('handles document deletion', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: mockDocuments
    });
    mockedAxios.delete.mockResolvedValueOnce({});

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    await waitFor(() => {
      expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    });

    const deleteButton = screen.getAllByRole('button', { name: /delete/i })[0];
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.queryByText('test1.pdf')).not.toBeInTheDocument();
      expect(mockedAxios.delete).toHaveBeenCalledWith(
        expect.stringContaining('/1')
      );
    });
  });

  it('displays error message on upload failure', async () => {
    const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    mockedAxios.post.mockRejectedValueOnce(new Error('Upload failed'));

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    const fileInput = screen.getByLabelText(/upload document/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('Error: Upload failed')).toBeInTheDocument();
    });
  });

  it('displays error message on deletion failure', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: mockDocuments
    });
    mockedAxios.delete.mockRejectedValueOnce(new Error('Deletion failed'));

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    await waitFor(() => {
      expect(screen.getByText('test1.pdf')).toBeInTheDocument();
    });

    const deleteButton = screen.getAllByRole('button', { name: /delete/i })[0];
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(screen.getByText('Error: Deletion failed')).toBeInTheDocument();
    });
  });

  it('displays loading state during upload', async () => {
    const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    mockedAxios.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    const fileInput = screen.getByLabelText(/upload document/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('displays loading state during document fetch', async () => {
    mockedAxios.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    expect(screen.getByRole('progressbar')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    });
  });

  it('handles file type validation', async () => {
    const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    const fileInput = screen.getByLabelText(/upload document/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('Only PDF files are allowed')).toBeInTheDocument();
    });
  });

  it('handles file size validation', async () => {
    const largeContent = 'a'.repeat(10 * 1024 * 1024); // 10MB
    const mockFile = new File([largeContent], 'test.pdf', { type: 'application/pdf' });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <DocumentManager />
      </Provider>
    );

    const fileInput = screen.getByLabelText(/upload document/i);
    fireEvent.change(fileInput, { target: { files: [mockFile] } });

    await waitFor(() => {
      expect(screen.getByText('File size must be less than 5MB')).toBeInTheDocument();
    });
  });
}); 