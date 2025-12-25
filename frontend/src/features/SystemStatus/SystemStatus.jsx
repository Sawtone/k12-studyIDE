import { useState, useEffect } from 'react'
import { Activity, Server, Database, Wifi, WifiOff, RefreshCw } from 'lucide-react'
import { healthCheck, getCapabilities } from '../../api/systemApi'

export const SystemStatus = ({ compact = false }) => {
  const [health, setHealth] = useState(null)
  const [capabilities, setCapabilities] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchStatus = async () => {
    setLoading(true)
    setError(null)
    try {
      const [healthData, capData] = await Promise.all([healthCheck(), getCapabilities()])
      setHealth(healthData)
      setCapabilities(capData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
    // 每 30 秒检查一次
    const interval = setInterval(fetchStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const isHealthy = health?.status === 'healthy'

  // 紧凑模式 - 只显示状态指示器
  if (compact) {
    return (
      <div className="flex items-center gap-1.5" title={isHealthy ? '系统正常' : '系统异常'}>
        <div className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'} ${loading ? 'animate-pulse' : ''}`} />
        {!loading && (
          <span className="text-[10px] text-gray-500">
            {isHealthy ? 'v' + (health?.version || '1.0') : '离线'}
          </span>
        )}
      </div>
    )
  }

  // 完整模式
  return (
    <div className="p-4 bg-white rounded-xl border border-gray-100">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity size={16} className="text-indigo-500" />
          <span className="text-sm font-medium text-gray-700">系统状态</span>
        </div>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="p-1 rounded hover:bg-gray-100 text-gray-400 hover:text-gray-600 disabled:opacity-50"
        >
          <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {error ? (
        <div className="flex items-center gap-2 text-red-500">
          <WifiOff size={14} />
          <span className="text-xs">连接失败</span>
        </div>
      ) : (
        <div className="space-y-2">
          {/* 整体状态 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wifi size={12} className={isHealthy ? 'text-green-500' : 'text-red-500'} />
              <span className="text-xs text-gray-600">服务状态</span>
            </div>
            <span className={`text-xs font-medium ${isHealthy ? 'text-green-600' : 'text-red-600'}`}>
              {isHealthy ? '正常' : '异常'}
            </span>
          </div>

          {/* 数据库 */}
          {health?.services?.database && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database size={12} className="text-gray-400" />
                <span className="text-xs text-gray-600">数据库</span>
              </div>
              <span className={`text-xs ${health.services.database === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {health.services.database === 'up' ? '正常' : '异常'}
              </span>
            </div>
          )}

          {/* Redis */}
          {health?.services?.redis && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server size={12} className="text-gray-400" />
                <span className="text-xs text-gray-600">缓存</span>
              </div>
              <span className={`text-xs ${health.services.redis === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {health.services.redis === 'up' ? '正常' : '异常'}
              </span>
            </div>
          )}

          {/* 版本 */}
          {health?.version && (
            <div className="pt-2 mt-2 border-t border-gray-100 text-[10px] text-gray-400">
              版本 {health.version} · {health.environment || 'production'}
            </div>
          )}

          {/* 支持的模式 */}
          {capabilities?.modes && (
            <div className="pt-2 mt-2 border-t border-gray-100">
              <div className="text-[10px] text-gray-400 mb-1">支持模式</div>
              <div className="flex gap-1">
                {capabilities.modes.map((mode) => (
                  <span
                    key={mode}
                    className="text-[9px] px-1.5 py-0.5 bg-indigo-50 text-indigo-600 rounded-full"
                  >
                    {mode === 'literature' ? '文学' : mode === 'science' ? '理科' : mode}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
