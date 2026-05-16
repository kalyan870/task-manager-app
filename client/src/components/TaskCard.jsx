import { useState } from 'react';
import { useTasks } from '../context/TaskContext';

const priorityColors = { low: 'bg-green-100 text-green-800', medium: 'bg-yellow-100 text-yellow-800', high: 'bg-red-100 text-red-800' };
const statusColors = { pending: 'bg-gray-100 text-gray-800', 'in-progress': 'bg-blue-100 text-blue-800', completed: 'bg-green-100 text-green-800' };

export default function TaskCard({ task, onEdit }) {
  const { updateTask, deleteTask } = useTasks();
  const [deleting, setDeleting] = useState(false);

  const handleStatusChange = async (e) => {
    await updateTask(task._id, { status: e.target.value });
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this task?')) return;
    setDeleting(true);
    try { await deleteTask(task._id); } catch { setDeleting(false); }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 hover:shadow-md transition">
      <div className="flex justify-between items-start mb-3">
        <h3 className="font-semibold text-gray-900 text-lg">{task.title}</h3>
        <div className="flex gap-2">
          <button onClick={() => onEdit(task)} className="text-indigo-600 hover:text-indigo-800 text-sm font-medium">Edit</button>
          <button onClick={handleDelete} disabled={deleting} className="text-red-500 hover:text-red-700 text-sm font-medium">
            {deleting ? '...' : 'Delete'}
          </button>
        </div>
      </div>
      {task.description && <p className="text-gray-600 text-sm mb-3">{task.description}</p>}
      <div className="flex flex-wrap gap-2 items-center">
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${priorityColors[task.priority]}`}>
          {task.priority}
        </span>
        <select
          value={task.status}
          onChange={handleStatusChange}
          className={`px-2.5 py-0.5 rounded-full text-xs font-medium border-0 cursor-pointer ${statusColors[task.status]}`}
        >
          <option value="pending">Pending</option>
          <option value="in-progress">In Progress</option>
          <option value="completed">Completed</option>
        </select>
        {task.dueDate && (
          <span className="text-xs text-gray-500">
            Due: {new Date(task.dueDate).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}
