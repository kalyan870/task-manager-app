import test from 'node:test';
import assert from 'node:assert/strict';
import { escapeRegex, pickTaskFields } from '../lib/task-input.js';

test('task writes keep only editable fields and drop owner/id injection', () => {
  assert.deepEqual(pickTaskFields({
    title: 'Review', user: 'other-user', _id: 'forged-id', isAdmin: true,
  }), { title: 'Review' });
});

test('task writes accept an empty body without throwing', () => {
  assert.deepEqual(pickTaskFields(undefined), {});
});

test('search text is treated literally as regex input', () => {
  const input = 'a.*(b)[c]';
  const escaped = escapeRegex(input);
  assert.ok(new RegExp(escaped).test(input));
  assert.equal(new RegExp(escaped).test('axxxb c'), false);
});
