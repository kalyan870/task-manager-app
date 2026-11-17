import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';
import { useAuth } from './AuthContext';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');
const API = `${API_BASE_URL}/api/tasks`;
const TaskContext = createContext();

export function TaskProvider({ children }) {
  const { user, getToken } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState({ status: '', priority: '', search: '' });

  const authHeaders = useCallback(async (extra = {}) => {
    const token = await getToken();
    if (!token) throw new Error('Sign in required');
    return { ...extra, Authorization: `Bearer ${token}` };
  }, [getToken]);

  useEffect(() => {
    let active = true;
    let connection;
    if (!user) {
      setTasks([]);
      return undefined;
    }
    getToken().then((token) => {
      if (!active || !token) return;
      connection = io(API_BASE_URL || '/', { auth: { token }, transports: ['websocket', 'polling'] });
      connection.on('taskCreated', (task) => setTasks((prev) => [task, ...prev.filter((item) => item._id !== task._id)]));
      connection.on('taskUpdated', (task) => setTasks((prev) => prev.map((item) => item._id === task._id ? task : item)));
      connection.on('taskDeleted', (id) => setTasks((prev) => prev.filter((item) => item._id !== id)));
    }).catch(() => {});
    return () => { active = false; connection?.close(); };
  }, [user?.id, getToken]);

  const fetchTasks = useCallback(async () => {
    if (!user) return setTasks([]);
    const params = new URLSearchParams();
    if (filter.status) params.set('status', filter.status);
    if (filter.priority) params.set('priority', filter.priority);
    if (filter.search) params.set('search', filter.search);
    const res = await fetch(`${API}?${params}`, { headers: await authHeaders() });
    if (!res.ok) throw new Error(res.status === 503 ? 'Task storage is not configured' : 'Could not load tasks');
    setTasks(await res.json());
  }, [user?.id, filter, authHeaders]);

  useEffect(() => { fetchTasks().catch(() => setTasks([])); }, [fetchTasks]);

  const createTask = async (taskData) => {
    const res = await fetch(API, {
      method: 'POST', headers: await authHeaders({ 'Content-Type': 'application/json' }), body: JSON.stringify(taskData),
    });
    if (!res.ok) throw new Error((await res.json()).message || 'Failed to create task');
    return res.json();
  };
  const updateTask = async (id, taskData) => {
    const res = await fetch(`${API}/${id}`, {
      method: 'PUT', headers: await authHeaders({ 'Content-Type': 'application/json' }), body: JSON.stringify(taskData),
    });
    if (!res.ok) throw new Error((await res.json()).message || 'Failed to update task');
    return res.json();
  };
  const deleteTask = async (id) => {
    const res = await fetch(`${API}/${id}`, { method: 'DELETE', headers: await authHeaders() });
    if (!res.ok) throw new Error((await res.json()).message || 'Failed to delete task');
  };

  return <TaskContext.Provider value={{ tasks, filter, setFilter, fetchTasks, createTask, updateTask, deleteTask }}>{children}</TaskContext.Provider>;
}

export const useTasks = () => useContext(TaskContext);
