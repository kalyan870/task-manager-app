import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { io } from 'socket.io-client';
import { useAuth } from './AuthContext';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '');
const API = `${API_BASE_URL}/api/tasks`;
let socket = null;

const TaskContext = createContext();

export function TaskProvider({ children }) {
  const { token } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState({ status: '', priority: '', search: '' });

  useEffect(() => {
    if (!token) {
      socket?.close();
      socket = null;
      return;
    }
    socket = io(API_BASE_URL || '/', { auth: { token }, transports: ['websocket', 'polling'] });
    return () => socket?.close();
  }, [token]);

  useEffect(() => {
    if (!socket) return;
    socket.on('taskCreated', (task) => setTasks((prev) => [task, ...prev]));
    socket.on('taskUpdated', (task) =>
      setTasks((prev) => prev.map((t) => (t._id === task._id ? task : t)))
    );
    socket.on('taskDeleted', (id) =>
      setTasks((prev) => prev.filter((t) => t._id !== id))
    );
    return () => {
      socket.off('taskCreated');
      socket.off('taskUpdated');
      socket.off('taskDeleted');
    };
  }, [token]);

  const fetchTasks = useCallback(async () => {
    if (!token) return;
    const params = new URLSearchParams();
    if (filter.status) params.set('status', filter.status);
    if (filter.priority) params.set('priority', filter.priority);
    if (filter.search) params.set('search', filter.search);
    const res = await fetch(`${API}?${params}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    setTasks(data);
  }, [token, filter]);

  useEffect(() => { fetchTasks(); }, [fetchTasks]);

  const createTask = async (taskData) => {
    const res = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(taskData),
    });
    if (!res.ok) throw new Error('Failed to create task');
    return res.json();
  };

  const updateTask = async (id, taskData) => {
    const res = await fetch(`${API}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(taskData),
    });
    if (!res.ok) throw new Error('Failed to update task');
    return res.json();
  };

  const deleteTask = async (id) => {
    const res = await fetch(`${API}/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to delete task');
  };

  return (
    <TaskContext.Provider value={{ tasks, filter, setFilter, fetchTasks, createTask, updateTask, deleteTask }}>
      {children}
    </TaskContext.Provider>
  );
}

export const useTasks = () => useContext(TaskContext);
