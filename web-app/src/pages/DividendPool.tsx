import DividendPoolView from '../components/DividendPoolView'

const DividendPool = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">分红殿堂</h1>
        <p className="text-gray-600">查看和管理灵值生态的分红池资金</p>
      </div>
      <DividendPoolView />
    </div>
  )
}

export default DividendPool
