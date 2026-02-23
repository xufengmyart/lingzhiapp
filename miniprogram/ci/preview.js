/**
 * 小程序代码预览脚本
 * 使用方法: npm run preview
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

// 预览配置
const previewConfig = {
  // 版本描述
  desc: process.env.DESC || '自动化预览',
  // 编译设置
  setting: {
    es6: true, // ES6 转 ES5
    es7: true, // 增强编译
    minify: false, // 预览时不压缩
    codeProtect: false,
    autoPrefixWXSS: true,
  },
  // 使用的 CI 机器人（1-30）
  robot: 1,
  // 二维码格式: 'image' | 'base64' | 'terminal'
  qrcodeFormat: 'image',
  // 二维码保存路径
  qrcodeOutputDest: path.resolve(__dirname, '../preview-qrcode.jpg'),
  // 预览页面路径（可选）
  pagePath: process.env.PAGE || 'pages/index/index',
  // 预览页面启动参数（可选）
  searchQuery: process.env.QUERY || '',
  // 场景值（默认 1011）
  scene: 1011,
  // 进度回调
  onProgressUpdate: (info) => {
    console.log(`[${new Date().toLocaleTimeString()}] ${info.message}`)
  }
}

async function preview() {
  console.log('========================================')
  console.log('开始生成小程序预览二维码')
  console.log('========================================')
  console.log(`AppID: ${projectConfig.appid}`)
  console.log(`描述: ${previewConfig.desc}`)
  console.log(`预览页面: ${previewConfig.pagePath}`)
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

    // 执行预览
    console.log('正在编译和生成预览二维码...\n')
    const previewResult = await ci.preview({
      project,
      desc: previewConfig.desc,
      setting: previewConfig.setting,
      robot: previewConfig.robot,
      qrcodeFormat: previewConfig.qrcodeFormat,
      qrcodeOutputDest: previewConfig.qrcodeOutputDest,
      pagePath: previewConfig.pagePath,
      searchQuery: previewConfig.searchQuery,
      scene: previewConfig.scene,
      onProgressUpdate: previewConfig.onProgressUpdate
    })

    // 输出结果
    console.log('\n========================================')
    console.log('✅ 预览二维码生成成功！')
    console.log('========================================')
    console.log('二维码路径:')
    console.log(`  ${previewConfig.qrcodeOutputDest}`)
    console.log('\n包信息:')
    if (previewResult.subPackageInfo) {
      previewResult.subPackageInfo.forEach(pkg => {
        console.log(`  ${pkg.name}: ${(pkg.size / 1024).toFixed(2)} KB`)
      })
    }
    if (previewResult.pluginInfo) {
      console.log('\n插件信息:')
      previewResult.pluginInfo.forEach(plugin => {
        console.log(`  ${plugin.pluginProviderAppid}: v${plugin.version} (${(plugin.size / 1024).toFixed(2)} KB)`)
      })
    }
    console.log('\n使用方法:')
    console.log('  1. 使用微信扫描上面的二维码')
    console.log('  2. 确认打开小程序预览')
    console.log('  3. 开始体验和测试')
    console.log('========================================\n')

    return previewResult
  } catch (error) {
    console.error('\n========================================')
    console.error('❌ 预览二维码生成失败！')
    console.error('========================================')
    console.error(`错误信息: ${error.message}`)
    console.error('\n常见问题排查:')
    console.error('  1. 检查 AppID 是否正确')
    console.error('  2. 检查私钥文件是否存在且路径正确')
    console.error('  3. 检查服务器 IP 是否在微信白名单中')
    console.error('  4. 检查项目路径是否正确')
    console.error('  5. 检查代码是否有语法错误')
    console.error('  6. 检查二维码保存目录是否存在')
    console.error('========================================\n')
    process.exit(1)
  }
}

// 执行预览
preview()
  .then(result => {
    console.log('预览流程完成！')
    process.exit(0)
  })
  .catch(error => {
    console.error('预览流程失败:', error)
    process.exit(1)
  })
