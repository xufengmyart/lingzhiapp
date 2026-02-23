import React, { useState, useEffect } from 'react';
import { userApi } from '../services/api';
import { User, CheckCircle, AlertCircle, Link as LinkIcon, Users } from 'lucide-react';

interface ReferralData {
  referrer_id: number;
  referrer_username: string;
  referrer_avatar: string;
}

interface ReferralCodeInputProps {
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  className?: string;
}

export const ReferralCodeInput: React.FC<ReferralCodeInputProps> = ({
  value,
  onChange,
  required = false,
  className = ''
}) => {
  const [validating, setValidating] = useState(false);
  const [valid, setValid] = useState<boolean | null>(null);
  const [referrerData, setReferrerData] = useState<ReferralData | null>(null);
  const [error, setError] = useState('');
  const [showError, setShowError] = useState(false);

  useEffect(() => {
    if (!value) {
      setValid(null);
      setReferrerData(null);
      setError('');
      setShowError(false);
      return;
    }

    // 防抖验证
    const timer = setTimeout(async () => {
      await validateReferralCode(value);
    }, 500);

    return () => clearTimeout(timer);
  }, [value]);

  const validateReferralCode = async (code: string) => {
    if (!code) {
      setValid(null);
      setReferrerData(null);
      setError('');
      setShowError(false);
      return;
    }

    setValidating(true);
    setValid(null);
    setError('');
    setShowError(false);

    try {
      const response = await userApi.validateReferralCode(code);
      setReferrerData(response.data);
      setValid(true);
    } catch (err: any) {
      console.error('验证推荐码失败:', err);
      setValid(false);
      setError(err.response?.data?.message || '推荐码无效');
      setShowError(true);
    } finally {
      setValidating(false);
    }
  };

  const handleBlur = () => {
    if (required && !value) {
      setError('请填写推荐码');
      setShowError(true);
      setValid(false);
    }
  };

  const renderStatusIcon = () => {
    if (validating) {
      return (
        <div className="text-xs text-indigo-400">验证中...</div>
      );
    }

    if (valid === true) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    }

    if (valid === false && showError) {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    }

    return <Users className="w-5 h-5 text-gray-300" />;
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <label className="block text-sm font-medium text-gray-200">
        推荐码 {required && <span className="text-red-500">*</span>}
      </label>
      
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Users className="h-5 w-5 text-gray-300" />
        </div>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onBlur={handleBlur}
          placeholder="请输入推荐码（例如：abc12345）"
          className={`
            block w-full pl-10 pr-10 py-3 border rounded-lg
            focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500
            transition-all duration-200
            placeholder-gray-600
            ${valid === true ? 'border-green-500 bg-green-50' : ''}
            ${valid === false ? 'border-red-500 bg-red-50' : ''}
            ${!value ? 'border-gray-400 bg-white/90' : 'bg-white/90'}
          `}
        />
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          {renderStatusIcon()}
        </div>
      </div>

      {/* 推荐人信息卡片 */}
      {valid === true && referrerData && (
        <div className="mt-3 p-4 bg-indigo-50 rounded-lg border border-indigo-200 flex items-center gap-3">
          <div className="flex-shrink-0">
            {referrerData.referrer_avatar ? (
              <img
                src={referrerData.referrer_avatar}
                alt={referrerData.referrer_username}
                className="w-12 h-12 rounded-full object-cover border-2 border-indigo-300"
              />
            ) : (
              <div className="w-12 h-12 rounded-full bg-indigo-200 flex items-center justify-center">
                <User className="w-6 h-6 text-indigo-600" />
              </div>
            )}
          </div>
          <div className="flex-grow">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-900">
                {referrerData.referrer_username}
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                <CheckCircle className="w-3 h-3 mr-1" />
                有效
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">推荐人</p>
          </div>
        </div>
      )}

      {/* 错误提示 */}
      {showError && error && (
        <div className="mt-2 flex items-center gap-2 text-sm text-red-400">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* 帮助文本 */}
      {valid === null && !value && (
        <div className="mt-2 flex items-start gap-2 text-xs text-gray-300">
          <LinkIcon className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <p>
            输入推荐码后，系统将自动验证推荐关系。
            扫描二维码时，推荐码会自动填充。
          </p>
        </div>
      )}
    </div>
  );
};
