/**
 * 小程序代码上传脚本
 * 使用方法: npm run upload
 */
const ci = require('miniprogram-ci')
const path = require('path')

// 配置信息
const projectConfig = {
  // 小程序 AppID（需要替换为实际的 AppID）
  appid: '请填写你的小程序AppID',
  // 项目路径（指向 miniprogram 目录）
  projectPath: path.resolve(__dirname, '../miniprogram'),
  // 私钥路径（需要从微信公众平台下载）
  privateKeyPath: path.resolve(__dirname, '../keys/private.xxx.key'),
  // 项目类型
  type: 'miniProgram'
}

// 上传配置
const uploadConfig = {
  // 版本号（可以通过命令行参数或环境变量指定）
  version: process.env.VERSION || `1.0.${new Date().toISOString().slice(0, 10).replace(/-/g, '')}`,
  // 版本描述
  desc: process.env.DESC || '自动化上传',
  // 编译设置
  setting: {
    es6: true, // ES6 转 ES5
    es7: true, // 增强编译
    minify: true, // 压缩代码
    codeProtect: false, // 代码保护
    autoPrefixWXSS: true, // 样式自动补全
  },
  // 使用的 CI 机器人（1-30）
  robot: 1,
  // 编译线程数
  threads: 1,
  // 进度回调
  onProgressUpdate: (info) => {
    console.log(`[${new Date().toLocaleTimeString()}] ${info.message}`)
  }
}

async function upload() {
  console.log('========================================')
  console.log('开始上传小程序代码')
  console.log('========================================')
  console.log(`AppID: ${projectConfig.appid}`)
  console.log(`版本: ${uploadConfig.version}`)
  console.log(`描述: ${uploadConfig.desc}`)
  console.log(`项目路径: ${projectConfig.projectPath}`)
  console.log('========================================\n')

  try {
    // 创建项目对象
    const project = new ci.Project({
      appid: projectConfig.appid,
      type: projectConfig.type,
      projectPath: projectConfig.projectPath,
      privateKeyPath: projectConfig.privateKeyPath,
      ignores: [
        'node_modules/**/*',
        '.git/**/*',
        '.gitignore',
        '.DS_Store',
        'project.private.config.json'
      ]
    })

    // 执行上传
    console.log('正在编译和上传...\n')
    const uploadResult = await ci.upload({
      project,
      version: uploadConfig.version,
      desc: uploadConfig.desc,
      setting: uploadConfig.setting,
      robot: uploadConfig.robot,
      threads: uploadConfig.threads,
      onProgressUpdate: uploadConfig.onProgressUpdate
    })

    // 输出结果
    console.log('\n========================================')
    console.log('✅ 上传成功！')
    console.log('========================================')
    console.log('版本信息:')
    console.log(`  版本号: ${uploadConfig.version}`)
    console.log(`  描述: ${uploadConfig.desc}`)
    console.log('\n包信息:')
    if (uploadResult.subPackageInfo) {
      uploadResult.subPackageInfo.forEach(pkg => {
        console.log(`  ${pkg.name}: ${(pkg.size / 1024).toFixed(2)} KB`)
      })
    }
    if (uploadResult.pluginInfo) {
      console.log('\n插件信息:')
      uploadResult.pluginInfo.forEach(plugin => {
        console.log(`  ${plugin.pluginProviderAppid}: v${plugin.version} (${(plugin.size / 1024).toFixed(2)} KB)`)
      })
    }
    console.log('\n下一步操作:')
    console.log('  1. 登录微信公众平台')
    console.log('  2. 进入「版本管理」')
    console.log('  3. 选择刚上传的版本')
    console.log('  4. 提交审核或设为体验版')
    console.log('========================================\n')

    return uploadResult
  } catch (error) {
    console.error('\n========================================')
    console.error('❌ 上传失败！')
    console.error('========================================')
    console.error(`错误信息: ${error.message}`)
    console.error('\n常见问题排查:')
    console.error('  1. 检查 AppID 是否正确')
    console.error('  2. 检查私钥文件是否存在且路径正确')
    console.error('  3. 检查服务器 IP 是否在微信白名单中')
    console.error('  4. 检查项目路径是否正确')
    console.error('  5. 检查代码是否有语法错误')
    console.error('========================================\n')
    process.exit(1)
  }
}

// 执行上传
upload()
  .then(result => {
    console.log('上传流程完成！')
    process.exit(0)
  })
  .catch(error => {
    console.error('上传流程失败:', error)
    process.exit(1)
  })
