import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import App from '../App';
import { useAuth } from '../hooks/useAuth';

// Mock useAuth hook
jest.mock('../hooks/useAuth');
const mockUseAuth = useAuth as jest.Mock;

// Create a mock store
const createMockStore = (initialState = {}) => {
  return configureStore({
    reducer: {
      auth: (state = initialState, action) => state,
      chat: (state = initialState, action) => state,
      documents: (state = initialState, action) => state
    }
  });
};

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login page when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      user: null,
      token: null
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.queryByText('Financial Assistant')).not.toBeInTheDocument();
  });

  it('renders chat interface when authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      },
      token: 'test-token'
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    expect(screen.getByText('Financial Assistant')).toBeInTheDocument();
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
  });

  it('redirects to login when accessing protected route while not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      user: null,
      token: null
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    // Try to access protected route
    window.history.pushState({}, '', '/chat');

    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('redirects to chat when accessing login while authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      },
      token: 'test-token'
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    // Try to access login page
    window.history.pushState({}, '', '/login');

    expect(screen.getByText('Financial Assistant')).toBeInTheDocument();
  });

  it('handles theme switching', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      },
      token: 'test-token'
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    const themeToggle = screen.getByRole('button', { name: /toggle theme/i });
    fireEvent.click(themeToggle);

    // Check if theme class is applied
    expect(document.documentElement).toHaveAttribute('data-theme', 'dark');
  });

  it('handles navigation between routes', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      },
      token: 'test-token'
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    // Navigate to documents page
    const documentsLink = screen.getByRole('link', { name: /documents/i });
    fireEvent.click(documentsLink);
    expect(screen.getByText('Document Manager')).toBeInTheDocument();

    // Navigate back to chat
    const chatLink = screen.getByRole('link', { name: /chat/i });
    fireEvent.click(chatLink);
    expect(screen.getByText('Financial Assistant')).toBeInTheDocument();
  });

  it('handles logout', () => {
    const mockLogout = jest.fn();
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      },
      token: 'test-token',
      logout: mockLogout
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    const logoutButton = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(logoutButton);

    expect(mockLogout).toHaveBeenCalled();
  });

  it('displays user information in header', () => {
    const mockUser = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      full_name: 'Test User'
    };

    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: mockUser,
      token: 'test-token'
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    expect(screen.getByText(mockUser.full_name)).toBeInTheDocument();
    expect(screen.getByText(mockUser.email)).toBeInTheDocument();
  });

  it('handles 404 routes', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User'
      },
      token: 'test-token'
    });

    const store = createMockStore();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </Provider>
    );

    // Navigate to non-existent route
    window.history.pushState({}, '', '/non-existent');

    expect(screen.getByText('404 - Page Not Found')).toBeInTheDocument();
  });
}); 