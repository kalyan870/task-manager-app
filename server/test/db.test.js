import test from 'node:test';
import assert from 'node:assert/strict';
import { createTaskRepository, getSql } from '../db.js';

test('Neon task queries bind owner, filters, and search input as parameters', async () => {
  const calls = [];
  const repo = createTaskRepository({ query: async (sql, params) => { calls.push({ sql, params }); return []; } });
  await repo.list('clerk_user_1', { status: 'pending', priority: 'high', search: "x%' OR 1=1 --" });
  assert.deepEqual(calls[0].params, ['clerk_user_1', 'pending', 'high', "x%' OR 1=1 --"]);
  assert.match(calls[0].sql, /owner_id = \$1/);
  assert.doesNotMatch(calls[0].sql, /clerk_user_1|OR 1=1/);
});

test('task mutation SQL always scopes rows by authenticated owner', async () => {
  const calls = [];
  const repo = createTaskRepository({ query: async (sql, params) => { calls.push({ sql, params }); return []; } });
  await repo.update('owner_A', '9', { title: 'new', description: '', status: 'pending', priority: 'medium', dueDate: null });
  await repo.remove('owner_B', '9');
  assert.ok(calls.every(({ sql }) => /owner_id\s*=\s*\$1/.test(sql)));
  assert.deepEqual(calls[0].params.slice(0, 2), ['owner_A', '9']);
  assert.deepEqual(calls[1].params, ['owner_B', '9']);
});

test('task storage refuses to start without a server-only Neon URL', () => {
  assert.throws(() => getSql({}), /DATABASE_URL is required/);
});
