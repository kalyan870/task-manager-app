import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <h1 className="text-xl font-bold text-indigo-600">TaskManager</h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 hidden sm:block">{user?.name}</span>
            <button
              onClick={logout}
              className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
