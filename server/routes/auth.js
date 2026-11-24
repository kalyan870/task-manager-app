import express from 'express';
import { protect } from '../middleware/auth.js';

const router = express.Router();
router.get('/me', protect, (req, res) => res.json({ id: req.userId }));
export default router;
