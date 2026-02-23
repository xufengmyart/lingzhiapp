// 临时文件：Profile页面身份证和银行卡信息显示补丁
// 请将以下代码段插入到 Profile.tsx 中的推荐人信息之后

// 在 "我的推荐人" 区域后，"注册时间" 之前，插入以下代码：

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <Shield className="w-5 h-5 text-gray-500" />
                <div className="flex-1">
                  <div className="text-xs text-gray-500">身份证号</div>
                  <div className="font-semibold">{isEditing ? (
                    <input
                      type="text"
                      value={formData.id_card || ''}
                      onChange={(e) => setFormData({ ...formData, id_card: e.target.value })}
                      placeholder="请输入身份证号（选填，用于提现验证）"
                      className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  ) : (
                    <span className="text-sm">
                      {formData.id_card 
                        ? formData.id_card.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
                        : '未设置'}
                    </span>
                  )}</div>
                </div>
              </div>

              <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg md:col-span-2">
                <Wallet className="w-5 h-5 text-gray-500" />
                <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <div className="text-xs text-gray-500">开户银行</div>
                    <div className="font-semibold">{isEditing ? (
                      <input
                        type="text"
                        value={formData.bank_name || ''}
                        onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                        placeholder="请输入开户银行"
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    ) : (formData.bank_name || '未设置')}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">银行账号</div>
                    <div className="font-semibold">{isEditing ? (
                      <input
                        type="text"
                        value={formData.bank_account || ''}
                        onChange={(e) => setFormData({ ...formData, bank_account: e.target.value })}
                        placeholder="请输入银行账号"
                        className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                      />
                    ) : (
                      formData.bank_account 
                        ? formData.bank_account.replace(/(\d{4})\d+(\d{4})/, '$1 **** **** $2')
                        : '未设置'
                    )}</div>
                  </div>
                </div>
              </div>

// 同时，确保 handleSave 函数中包含这些字段的保存：
/*
  const handleSave = async () => {
    try {
      const response = await userApi.updateProfile({
        username: formData.username,
        email: formData.email,
        phone: formData.phone,
        real_name: formData.real_name,
        avatar_url: formData.avatar_url,
        title: formData.title,
        position: formData.position,
        gender: formData.gender,
        bio: formData.bio,
        location: formData.location,
        website: formData.website,
        id_card: formData.id_card,
        bank_account: formData.bank_account,
        bank_name: formData.bank_name,
      })
      ...
    }
  }
*/
