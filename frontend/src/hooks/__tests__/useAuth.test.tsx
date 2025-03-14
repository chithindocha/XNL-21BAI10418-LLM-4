import { renderHook, act } from '@testing-library/react';
import { useAuth, AuthProvider } from '../useAuth';
import axios from 'axios';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('useAuth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('provides initial state', () => {
    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('handles successful login', async () => {
    const mockUser = {
      username: 'testuser',
      email: 'test@example.com',
      full_name: 'Test User',
    };

    const mockToken = 'test-token';

    mockedAxios.post.mockResolvedValueOnce({
      data: { access_token: mockToken },
    });

    mockedAxios.get.mockResolvedValueOnce({
      data: mockUser,
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await act(async () => {
      await result.current.login('testuser', 'testpass');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe(mockToken);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(localStorage.getItem('token')).toBe(mockToken);
  });

  it('handles login error', async () => {
    const errorMessage = 'Invalid credentials';
    mockedAxios.post.mockRejectedValueOnce(new Error(errorMessage));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await act(async () => {
      try {
        await result.current.login('testuser', 'wrongpass');
      } catch (error) {
        // Expected error
      }
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe(errorMessage);
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('handles logout', async () => {
    // First login
    const mockUser = {
      username: 'testuser',
      email: 'test@example.com',
      full_name: 'Test User',
    };

    const mockToken = 'test-token';

    mockedAxios.post.mockResolvedValueOnce({
      data: { access_token: mockToken },
    });

    mockedAxios.get.mockResolvedValueOnce({
      data: mockUser,
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    await act(async () => {
      await result.current.login('testuser', 'testpass');
    });

    // Then logout
    await act(async () => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('restores session from localStorage', async () => {
    const mockUser = {
      username: 'testuser',
      email: 'test@example.com',
      full_name: 'Test User',
    };

    const mockToken = 'test-token';
    localStorage.setItem('token', mockToken);

    mockedAxios.get.mockResolvedValueOnce({
      data: mockUser,
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // Wait for the effect to run
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.token).toBe(mockToken);
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('handles session restoration error', async () => {
    const mockToken = 'test-token';
    localStorage.setItem('token', mockToken);

    mockedAxios.get.mockRejectedValueOnce(new Error('Session expired'));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // Wait for the effect to run
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });

    expect(result.current.user).toBeNull();
    expect(result.current.token).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Session expired');
    expect(localStorage.getItem('token')).toBeNull();
  });

  it('handles loading state during login', async () => {
    mockedAxios.post.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    act(() => {
      result.current.login('testuser', 'testpass');
    });

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('handles loading state during session restoration', async () => {
    const mockToken = 'test-token';
    localStorage.setItem('token', mockToken);

    mockedAxios.get.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    expect(result.current.isLoading).toBe(true);

    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });

    expect(result.current.isLoading).toBe(false);
  });

  it('clears error on successful operation', async () => {
    const errorMessage = 'Previous error';
    const mockUser = {
      username: 'testuser',
      email: 'test@example.com',
      full_name: 'Test User',
    };

    const mockToken = 'test-token';

    mockedAxios.post.mockResolvedValueOnce({
      data: { access_token: mockToken },
    });

    mockedAxios.get.mockResolvedValueOnce({
      data: mockUser,
    });

    const { result } = renderHook(() => useAuth(), {
      wrapper: AuthProvider,
    });

    // Set initial error
    act(() => {
      result.current.setError(errorMessage);
    });

    expect(result.current.error).toBe(errorMessage);

    // Perform successful login
    await act(async () => {
      await result.current.login('testuser', 'testpass');
    });

    expect(result.current.error).toBeNull();
  });
}); 