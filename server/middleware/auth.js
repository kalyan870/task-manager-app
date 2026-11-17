import { verifyToken } from '@clerk/backend';

const bearerToken = (header = '') => {
  const match = /^Bearer\s+([A-Za-z0-9._-]+)$/i.exec(header);
  return match?.[1] || null;
};

export function createRequireUser({ verify = verifyToken, env = process.env } = {}) {
  return async function requireUser(req, res, next) {
    const token = bearerToken(req.headers.authorization);
    if (!token) return res.status(401).json({ message: 'Sign in required' });
    const authorizedParties = (env.CLERK_AUTHORIZED_PARTIES || env.CLIENT_ORIGINS || '')
      .split(',').map((origin) => origin.trim()).filter(Boolean);
    if ((!env.CLERK_SECRET_KEY && !env.CLERK_JWT_KEY) || !authorizedParties.length) {
      return res.status(503).json({ message: 'Authentication is not configured' });
    }
    try {
      const claims = await verify(token, {
        secretKey: env.CLERK_SECRET_KEY,
        jwtKey: env.CLERK_JWT_KEY,
        authorizedParties,
      });
      if (typeof claims.sub !== 'string' || !claims.sub) return res.status(401).json({ message: 'Invalid session' });
      req.userId = claims.sub;
      return next();
    } catch {
      return res.status(401).json({ message: 'Invalid or expired session' });
    }
  };
}

export const protect = createRequireUser();
