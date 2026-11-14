import express from 'express';
import Task from '../models/Task.js';
import { protect } from '../middleware/auth.js';
import { escapeRegex, pickTaskFields } from '../lib/task-input.js';

const router = express.Router();

router.use(protect);

router.get('/', async (req, res) => {
  try {
    const { status, priority, search } = req.query;
    const filter = { user: req.user._id };
    if (status) filter.status = status;
    if (priority) filter.priority = priority;
    if (typeof search === 'string' && search.trim()) {
      filter.title = { $regex: escapeRegex(search.trim().slice(0, 100)), $options: 'i' };
    }
    const tasks = await Task.find(filter).sort({ createdAt: -1 });
    res.json(tasks);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const task = await Task.create({ ...pickTaskFields(req.body), user: req.user._id });
    req.app.get('io').to(`user:${req.user._id}`).emit('taskCreated', task);
    res.status(201).json(task);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const updates = pickTaskFields(req.body);
    const task = await Task.findOneAndUpdate(
      { _id: req.params.id, user: req.user._id },
      updates,
      { new: true, runValidators: true }
    );
    if (!task) return res.status(404).json({ message: 'Task not found' });
    req.app.get('io').to(`user:${req.user._id}`).emit('taskUpdated', task);
    res.json(task);
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const task = await Task.findOneAndDelete({ _id: req.params.id, user: req.user._id });
    if (!task) return res.status(404).json({ message: 'Task not found' });
    req.app.get('io').to(`user:${req.user._id}`).emit('taskDeleted', task._id);
    res.json({ message: 'Task deleted' });
  } catch (err) {
    res.status(500).json({ message: err.message });
  }
});

export default router;
