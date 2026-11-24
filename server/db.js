import { neon } from '@neondatabase/serverless';

let client;
export function getSql(env = process.env) {
  if (!env.DATABASE_URL) {
    const error = new Error('DATABASE_URL is required for durable task storage.');
    error.code = 'DATABASE_NOT_CONFIGURED';
    throw error;
  }
  if (env === process.env) client ??= neon(env.DATABASE_URL);
  return client || neon(env.DATABASE_URL);
}

const toTask = (row) => row && ({
  _id: String(row.id), user: row.owner_id, title: row.title, description: row.description,
  status: row.status, priority: row.priority, dueDate: row.due_date,
  createdAt: row.created_at, updatedAt: row.updated_at,
});

export function createTaskRepository(sql) {
  return {
    async list(userId, { status, priority, search }) {
      const where = ['owner_id = $1'];
      const params = [userId];
      if (status) { params.push(status); where.push(`status = $${params.length}`); }
      if (priority) { params.push(priority); where.push(`priority = $${params.length}`); }
      if (search) { params.push(search); where.push(`position(lower($${params.length}) in lower(title)) > 0`); }
      const rows = await sql.query(`SELECT id, owner_id, title, description, status, priority, due_date, created_at, updated_at FROM tasks WHERE ${where.join(' AND ')} ORDER BY created_at DESC`, params);
      return rows.map(toTask);
    },
    async create(userId, values) {
      const rows = await sql.query(
        'INSERT INTO tasks (owner_id,title,description,status,priority,due_date) VALUES ($1,$2,$3,$4,$5,$6) RETURNING id,owner_id,title,description,status,priority,due_date,created_at,updated_at',
        [userId, values.title, values.description, values.status, values.priority, values.dueDate],
      );
      return toTask(rows[0]);
    },
    async update(userId, id, values) {
      const rows = await sql.query(
        'UPDATE tasks SET title=$3,description=$4,status=$5,priority=$6,due_date=$7,updated_at=now() WHERE owner_id=$1 AND id=$2 RETURNING id,owner_id,title,description,status,priority,due_date,created_at,updated_at',
        [userId, id, values.title, values.description, values.status, values.priority, values.dueDate],
      );
      return toTask(rows[0]);
    },
    async remove(userId, id) {
      const rows = await sql.query('DELETE FROM tasks WHERE owner_id=$1 AND id=$2 RETURNING id', [userId, id]);
      return rows.length > 0;
    },
  };
}

export const taskRepository = {
  list: (...args) => createTaskRepository(getSql()).list(...args),
  create: (...args) => createTaskRepository(getSql()).create(...args),
  update: (...args) => createTaskRepository(getSql()).update(...args),
  remove: (...args) => createTaskRepository(getSql()).remove(...args),
};

