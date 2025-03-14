import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import ChatInterface from '../ChatInterface';
import { useAuth } from '../../hooks/useAuth';
import { io } from 'socket.io-client';

// Mock socket.io-client
jest.mock('socket.io-client');
const mockSocket = {
  on: jest.fn(),
  emit: jest.fn(),
  disconnect: jest.fn(),
};
(io as jest.Mock).mockReturnValue(mockSocket);

// Mock useAuth hook
jest.mock('../../hooks/useAuth');
const mockUseAuth = useAuth as jest.Mock;
mockUseAuth.mockReturnValue({
  token: 'test-token',
  user: {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    full_name: 'Test User'
  }
});

// Create a mock store
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      chat: (state = initialState, action) => state
    }
  });
};

describe('ChatInterface', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat interface correctly', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    expect(screen.getByText('Financial Assistant')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('handles message input and submission', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(mockSocket.emit).toHaveBeenCalledWith('message', {
      type: 'message',
      content: 'Test message'
    });
    expect(input).toHaveValue('');
  });

  it('displays loading state while waiting for response', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });

    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(sendButton);

    expect(screen.getByText('Thinking...')).toBeInTheDocument();

    // Simulate response
    mockSocket.on.mock.calls.find(call => call[0] === 'message')[1]({
      type: 'message',
      content: 'Response message',
      is_user: false
    });

    await waitFor(() => {
      expect(screen.queryByText('Thinking...')).not.toBeInTheDocument();
    });
  });

  it('displays error message when socket connection fails', () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    // Simulate socket error
    mockSocket.on.mock.calls.find(call => call[0] === 'error')[1](new Error('Connection failed'));

    expect(screen.getByText('Error: Connection failed')).toBeInTheDocument();
  });

  it('scrolls to bottom when new messages arrive', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    const messagesContainer = screen.getByTestId('messages-container');
    const scrollToMock = jest.fn();
    Object.defineProperty(messagesContainer, 'scrollTo', {
      value: scrollToMock
    });

    // Simulate new message
    mockSocket.on.mock.calls.find(call => call[0] === 'message')[1]({
      type: 'message',
      content: 'New message',
      is_user: false
    });

    await waitFor(() => {
      expect(scrollToMock).toHaveBeenCalled();
    });
  });

  it('handles typing indicator', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    const input = screen.getByPlaceholderText('Type your message...');

    fireEvent.change(input, { target: { value: 'T' } });

    expect(mockSocket.emit).toHaveBeenCalledWith('typing', {
      type: 'typing',
      is_typing: true
    });

    // Simulate typing indicator from other user
    mockSocket.on.mock.calls.find(call => call[0] === 'typing')[1]({
      type: 'typing',
      is_typing: true,
      user_id: 2
    });

    expect(screen.getByText('Someone is typing...')).toBeInTheDocument();
  });

  it('displays system messages', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    // Simulate system message
    mockSocket.on.mock.calls.find(call => call[0] === 'system')[1]({
      type: 'system',
      message: 'User joined the chat'
    });

    expect(screen.getByText('User joined the chat')).toBeInTheDocument();
  });

  it('clears chat history', async () => {
    const store = createMockStore();
    render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    const clearButton = screen.getByRole('button', { name: /clear chat/i });
    fireEvent.click(clearButton);

    expect(mockSocket.emit).toHaveBeenCalledWith('clear_history');
  });

  it('disconnects socket on unmount', () => {
    const store = createMockStore();
    const { unmount } = render(
      <Provider store={store}>
        <ChatInterface />
      </Provider>
    );

    unmount();
    expect(mockSocket.disconnect).toHaveBeenCalled();
  });
}); 