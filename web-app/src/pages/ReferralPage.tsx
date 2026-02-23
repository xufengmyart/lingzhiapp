import React, { useState, useEffect } from 'react';
import { userApi } from '../services/api';
import { QrCode, Download, Share2, Copy } from 'lucide-react';

interface ReferralData {
  referral_code: string;
  qrcode: string;
  referral_url: string;
}

export const ReferralPage: React.FC = () => {
  const [referralData, setReferralData] = useState<ReferralData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [downloading, setDownloading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let mounted = true;
    
    const loadReferralData = async () => {
      try {
        setLoading(true);
        const response = await userApi.getReferralQrcode(false);
        if (mounted) {
          if ('data' in response) {
            setReferralData(response.data);
          }
        }
      } catch (err: any) {
        if (mounted) {
          setError(err.message || '加载推荐码失败');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    loadReferralData();
    
    return () => {
      mounted = false;
    };
  }, []);

  const handleDownload = async () => {
    if (!referralData) return;
    
    try {
      setDownloading(true);
      const response = await userApi.getReferralQrcode(true);
      if ('blob' in response) {
        const { blob } = response;
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `推荐码_${referralData.referral_code}.png`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err: any) {
      setError(err.message || '下载失败');
    } finally {
      setDownloading(false);
    }
  };

  const handleCopyLink = () => {
    if (referralData && referralData.referral_url) {
      navigator.clipboard.writeText(referralData.referral_url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleShare = async () => {
    if (!referralData) return;
    
    if (navigator.share && referralData.referral_url) {
      try {
        await navigator.share({
          title: '邀请你加入灵值生态园',
          text: `使用我的推荐码 ${referralData.referral_code} 注册，享受更多权益！`,
          url: referralData.referral_url
        });
      } catch (err) {
        console.log('分享取消', err);
      }
    } else {
      handleCopyLink();
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            刷新页面
          </button>
        </div>
      </div>
    );
  }

  const referralCode = referralData?.referral_code || '';
  const referralUrl = referralData?.referral_url || '';
  const qrcodeData = referralData?.qrcode || '';

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {/* 头部 */}
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-8 text-center text-white">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <Share2 className="w-8 h-8" />
            </div>
            <h1 className="text-2xl font-bold mb-2">我的推荐码</h1>
            <p className="text-indigo-100">邀请好友注册，共享生态红利</p>
          </div>

          {/* 内容 */}
          <div className="p-6">
            {/* 推荐码 */}
            <div className="mb-6 text-center">
              <p className="text-sm text-gray-500 mb-2">推荐码</p>
              <div className="inline-block bg-indigo-50 px-6 py-3 rounded-lg">
                <span className="text-3xl font-bold text-indigo-600 tracking-wider">
                  {referralCode}
                </span>
              </div>
            </div>

            {/* 二维码 */}
            <div className="mb-6">
              <div className="bg-white border-2 border-dashed border-gray-200 rounded-xl p-6">
                <div className="flex justify-center">
                  {qrcodeData && (
                    <img
                      src={qrcodeData}
                      alt="推荐二维码"
                      className="w-64 h-64 object-contain"
                    />
                  )}
                </div>
                <p className="text-center text-xs text-gray-500 mt-3">
                  扫描二维码，快速注册
                </p>
              </div>
            </div>

            {/* 推荐链接 */}
            <div className="mb-6">
              <p className="text-sm text-gray-500 mb-2">推荐链接</p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={referralUrl}
                  readOnly
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
                />
                <button
                  onClick={handleCopyLink}
                  className="px-4 py-2 bg-indigo-100 text-indigo-600 rounded-lg hover:bg-indigo-200"
                >
                  <Copy className="w-4 h-4 inline mr-1" />
                  {copied ? '已复制' : '复制'}
                </button>
              </div>
            </div>

            {/* 操作按钮 */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={handleDownload}
                disabled={downloading}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-5 h-5" />
                <span>{downloading ? '下载中...' : '保存二维码'}</span>
              </button>
              <button
                onClick={handleShare}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                <Share2 className="w-5 h-5" />
                <span>分享</span>
              </button>
            </div>
          </div>

          {/* 底部提示 */}
          <div className="px-6 py-4 bg-gray-50">
            <p className="text-xs text-gray-500 text-center">
              💡 提示：通过您的推荐码或二维码注册的用户将自动成为您的下级
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReferralPage;
