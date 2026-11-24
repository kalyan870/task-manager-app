import express from 'express';
import { taskRepository } from '../db.js';
import { protect } from '../middleware/auth.js';

const router = express.Router();
router.use(protect);
const statuses = new Set(['pending', 'in-progress', 'completed']);
const priorities = new Set(['low', 'medium', 'high']);
const validId = (value) => /^\d+$/.test(value) && Number(value) > 0;
const fail = (res) => res.status(503).json({ message: 'Task storage is temporarily unavailable' });
const parseTask = (body = {}) => {
  const title = typeof body.title === 'string' ? body.title.trim() : '';
  const description = typeof body.description === 'string' ? body.description : '';
  const status = body.status ?? 'pending';
  const priority = body.priority ?? 'medium';
  const dueDate = body.dueDate ?? body.due_date ?? null;
  if (!title || title.length > 200 || description.length > 5000 || !statuses.has(status) || !priorities.has(priority)) return null;
  if (dueDate !== null && (typeof dueDate !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(dueDate))) return null;
  return { title, description, status, priority, dueDate };
};

router.get('/', async (req, res) => {
  const { status, priority, search } = req.query;
  if (status && !statuses.has(status)) return res.status(400).json({ message: 'Invalid status' });
  if (priority && !priorities.has(priority)) return res.status(400).json({ message: 'Invalid priority' });
  try {
    return res.json(await taskRepository.list(req.userId, {
      status, priority, search: typeof search === 'string' ? search.trim().slice(0, 100) : '',
    }));
  } catch { return fail(res); }
});

router.post('/', async (req, res) => {
  const values = parseTask(req.body);
  if (!values) return res.status(400).json({ message: 'Provide valid task details' });
  try {
    const task = await taskRepository.create(req.userId, values);
    req.app.get('io').to(`user:${req.userId}`).emit('taskCreated', task);
    return res.status(201).json(task);
  } catch { return fail(res); }
});

router.put('/:id', async (req, res) => {
  if (!validId(req.params.id)) return res.status(400).json({ message: 'Invalid task id' });
  const values = parseTask(req.body);
  if (!values) return res.status(400).json({ message: 'Provide valid task details' });
  try {
    const task = await taskRepository.update(req.userId, req.params.id, values);
    if (!task) return res.status(404).json({ message: 'Task not found' });
    req.app.get('io').to(`user:${req.userId}`).emit('taskUpdated', task);
    return res.json(task);
  } catch { return fail(res); }
});

router.delete('/:id', async (req, res) => {
  if (!validId(req.params.id)) return res.status(400).json({ message: 'Invalid task id' });
  try {
    if (!(await taskRepository.remove(req.userId, req.params.id))) return res.status(404).json({ message: 'Task not found' });
    req.app.get('io').to(`user:${req.userId}`).emit('taskDeleted', req.params.id);
    return res.json({ message: 'Task deleted' });
  } catch { return fail(res); }
});

export default router;
