import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequireUser } from '../middleware/auth.js';

const response = () => ({ statusCode: 200, body: null, status(code) { this.statusCode = code; return this; }, json(body) { this.body = body; return this; } });
const configured = { CLERK_JWT_KEY: 'test-public-key', CLERK_AUTHORIZED_PARTIES: 'https://app.example' };

test('private API rejects missing bearer session', async () => {
  const res = response();
  await createRequireUser({ env: configured })({ headers: {} }, res, () => assert.fail('must reject'));
  assert.equal(res.statusCode, 401);
});

test('private API returns unavailable until Clerk verification is configured', async () => {
  const res = response();
  await createRequireUser({ env: {} })({ headers: { authorization: 'Bearer forged.token' } }, res, () => assert.fail('must reject'));
  assert.equal(res.statusCode, 503);
});

test('verified Clerk subject is the only task owner identity', async () => {
  const res = response();
  let verifiedOptions;
  let nextCalled = false;
  const requireUser = createRequireUser({
    env: configured,
    verify: async (_token, options) => { verifiedOptions = options; return { sub: 'user_verified' }; },
  });
  await requireUser({ headers: { authorization: 'Bearer valid.token' } }, res, () => { nextCalled = true; });
  assert.equal(nextCalled, true);
  assert.equal(res.statusCode, 200);
  assert.equal(res.body, null);
  assert.equal(verifiedOptions.authorizedParties[0], 'https://app.example');
});

test('forged token fails closed', async () => {
  const res = response();
  const requireUser = createRequireUser({ env: configured, verify: async () => { throw new Error('bad signature'); } });
  await requireUser({ headers: { authorization: 'Bearer forged.token' } }, res, () => assert.fail('must reject'));
  assert.equal(res.statusCode, 401);
});
