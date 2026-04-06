export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 space-y-4">
      <div className="w-10 h-10 border-4 border-gray-700 border-t-red-500 rounded-full animate-spin" />
      <p className="text-gray-400">{message}</p>
    </div>
  )
}
