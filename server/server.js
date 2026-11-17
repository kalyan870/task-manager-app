import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import { verifyToken } from '@clerk/backend';
import authRoutes from './routes/auth.js';
import taskRoutes from './routes/tasks.js';

const app = express();
const httpServer = createServer(app);
const allowedOrigins = (process.env.CLIENT_ORIGINS || 'http://localhost:3000')
  .split(',').map((origin) => origin.trim()).filter(Boolean);
const clerkOptions = {
  secretKey: process.env.CLERK_SECRET_KEY,
  jwtKey: process.env.CLERK_JWT_KEY,
  authorizedParties: (process.env.CLERK_AUTHORIZED_PARTIES || process.env.CLIENT_ORIGINS || '')
    .split(',').map((origin) => origin.trim()).filter(Boolean),
};
const verifySession = async (token) => {
  if ((!clerkOptions.secretKey && !clerkOptions.jwtKey) || !clerkOptions.authorizedParties.length) {
    throw new Error('Clerk verification is not configured');
  }
  return verifyToken(token, clerkOptions);
};

const io = new Server(httpServer, { cors: { origin: allowedOrigins, methods: ['GET', 'POST'] } });
app.set('io', io);
app.use(cors({ origin: allowedOrigins }));
app.use(express.json({ limit: '32kb' }));
app.get('/health', (_req, res) => res.json({ ok: true }));

io.use(async (socket, next) => {
  const token = socket.handshake.auth?.token;
  if (typeof token !== 'string') return next(new Error('Authentication required'));
  try {
    const claims = await verifySession(token);
    if (typeof claims.sub !== 'string' || !claims.sub) return next(new Error('Authentication failed'));
    socket.data.userId = claims.sub;
    return next();
  } catch { return next(new Error('Authentication failed')); }
});
app.use('/api/auth', authRoutes);
app.use('/api/tasks', taskRoutes);

io.on('connection', (socket) => socket.join(`user:${socket.data.userId}`));

const PORT = Number(process.env.PORT || 5000);
if (!process.env.DATABASE_URL) throw new Error('DATABASE_URL is required');
httpServer.listen(PORT, () => console.log(`Server running on port ${PORT}`));
