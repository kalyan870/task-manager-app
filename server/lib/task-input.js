export const editableTaskFields = ['title', 'description', 'status', 'priority', 'dueDate'];

export function pickTaskFields(body) {
  return Object.fromEntries(Object.entries(body || {})
    .filter(([key]) => editableTaskFields.includes(key)));
}

export function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
