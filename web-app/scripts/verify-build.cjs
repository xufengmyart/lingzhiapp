#!/usr/bin/env node

/**
 * 构建验证脚本
 * 
 * 功能：
 * 1. 检查构建文件是否存在
 * 2. 检查版本信息是否正确
 * 3. 检查 Service Worker 是否更新
 */

const fs = require('fs');
const path = require('path');

const PROJECT_DIR = path.resolve(__dirname, '..');
const DIST_DIR = path.join(PROJECT_DIR, 'dist');
const VERSION_FILE = path.join(DIST_DIR, 'version.json');
const SW_FILE = path.join(DIST_DIR, 'sw.js');

// 颜色输出
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m'
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logError(message) {
  log(`[ERROR] ${message}`, colors.red);
}

function logSuccess(message) {
  log(`[SUCCESS] ${message}`, colors.green);
}

function logWarning(message) {
  log(`[WARNING] ${message}`, colors.yellow);
}

function logInfo(message) {
  log(`[INFO] ${message}`, colors.blue);
}

// 主函数
function main() {
  console.log('');
  log('========================================', colors.blue);
  log('构建验证', colors.blue);
  log('========================================', colors.blue);
  console.log('');

  let errors = 0;
  let warnings = 0;

  // 1. 检查构建目录是否存在
  if (!fs.existsSync(DIST_DIR)) {
    logError('构建目录不存在: ' + DIST_DIR);
    errors++;
  } else {
    logSuccess('构建目录存在');
  }

  // 2. 检查版本文件是否存在
  if (!fs.existsSync(VERSION_FILE)) {
    logError('版本文件不存在: ' + VERSION_FILE);
    errors++;
  } else {
    logSuccess('版本文件存在');
    
    try {
      const versionInfo = JSON.parse(fs.readFileSync(VERSION_FILE, 'utf-8'));
      logInfo(`版本号: ${versionInfo.version}`);
      logInfo(`构建时间: ${versionInfo.buildTime}`);
      
      // 检查版本号格式
      if (!/^\d{8}-\d{4}$/.test(versionInfo.version)) {
        logWarning('版本号格式不正确，应该是 YYYYMMDD-HHMM');
        warnings++;
      }
    } catch (error) {
      logError('版本文件格式错误: ' + error.message);
      errors++;
    }
  }

  // 3. 检查 Service Worker 是否存在
  if (!fs.existsSync(SW_FILE)) {
    logError('Service Worker 不存在: ' + SW_FILE);
    errors++;
  } else {
    logSuccess('Service Worker 存在');
    
    try {
      const swContent = fs.readFileSync(SW_FILE, 'utf-8');
      
      // 检查是否包含版本号
      if (swContent.includes('VERSION = ')) {
        const versionMatch = swContent.match(/VERSION = '(\d{8}-\d{4})'/);
        if (versionMatch) {
          logInfo(`Service Worker 版本: ${versionMatch[1]}`);
        } else {
          logWarning('Service Worker 版本号格式不正确');
          warnings++;
        }
      } else {
        logWarning('Service Worker 未包含版本号');
        warnings++;
      }
    } catch (error) {
      logError('读取 Service Worker 失败: ' + error.message);
      errors++;
    }
  }

  // 4. 检查关键文件
  const keyFiles = [
    'index.html',
    'assets/index.js',
    'assets/index.css'
  ];

  console.log('');
  logInfo('检查关键文件...');
  for (const file of keyFiles) {
    const filePath = path.join(DIST_DIR, file);
    if (fs.existsSync(filePath)) {
      const stats = fs.statSync(filePath);
      const size = (stats.size / 1024).toFixed(2);
      logSuccess(`  ${file} (${size} KB)`);
    } else {
      logWarning(`  ${file} 不存在`);
      warnings++;
    }
  }

  console.log('');
  log('========================================', colors.blue);
  if (errors === 0 && warnings === 0) {
    logSuccess('构建验证通过');
    log('========================================', colors.blue);
    process.exit(0);
  } else if (errors === 0) {
    logWarning(`构建验证通过，但有 ${warnings} 个警告`);
    log('========================================', colors.blue);
    process.exit(0);
  } else {
    logError(`构建验证失败，有 ${errors} 个错误`);
    log('========================================', colors.blue);
    process.exit(1);
  }
}

// 执行主函数
main();
