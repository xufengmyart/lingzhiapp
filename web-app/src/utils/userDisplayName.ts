/**
 * 用户名称显示工具
 * 统一处理用户名称的显示，避免显示"用户1"、"用户2"等格式
 */

/**
 * 获取用户的显示名称
 * @param userId 用户ID
 * @param username 用户名（可选）
 * @returns 显示名称（注册用户 + ID 或原始用户名）
 */
export function getUserDisplayName(userId?: number | string, username?: string): string {
  if (!userId) return '注册用户';
  
  // 如果有原始用户名且不是"用户X"格式，则使用原始用户名
  if (username && !/^用户\d+$/.test(username)) {
    return username;
  }
  
  // 否则返回"注册用户"格式
  return `注册用户`;
}

/**
 * 格式化作者名称
 * @param author 作者名称
 * @param authorId 作者ID（可选）
 * @returns 格式化后的作者名称
 */
export function formatAuthorName(author?: string, authorId?: number): string {
  if (!author) return '系统';
  
  // 如果是"用户X"格式，转换为"注册用户"
  if (/^用户\d+$/.test(author)) {
    return '注册用户';
  }
  
  return author;
}

/**
 * 获取用户的详细显示名称（包含ID）
 * @param userId 用户ID
 * @param username 用户名（可选）
 * @returns 详细显示名称
 */
export function getUserDetailedDisplayName(userId?: number | string, username?: string): string {
  if (!userId) return '注册用户';
  
  const displayName = getUserDisplayName(userId, username);
  const id = typeof userId === 'number' ? userId : parseInt(userId, 10);
  
  // 如果是数字ID，添加到显示名称中
  if (!isNaN(id) && id > 0) {
    return displayName;
  }
  
  return displayName;
}

/**
 * 格式化用户列表显示（避免显示多个"用户1"、"用户2"等）
 * @param users 用户列表 [{id: 1, username: '用户1'}, {id: 2, username: '用户2'}]
 * @param maxDisplay 最大显示数量，默认3
 * @returns 格式化后的字符串
 */
export function formatUserListDisplay(
  users: Array<{ id?: number | string; username?: string }>,
  maxDisplay: number = 3
): string {
  if (!users || users.length === 0) return '暂无用户';
  
  const displayNames = users
    .slice(0, maxDisplay)
    .map(user => getUserDisplayName(user.id, user.username))
    .filter(name => name); // 过滤掉空值
  
  if (displayNames.length === 0) return '注册用户';
  
  // 如果所有显示名称都是"注册用户"，则统一显示为"注册用户"
  const allSame = displayNames.every(name => name === '注册用户');
  if (allSame) {
    return users.length > 1 ? `注册用户 (${users.length})` : '注册用户';
  }
  
  const namesStr = displayNames.join('、');
  
  if (users.length > maxDisplay) {
    return `${namesStr} 等 ${users.length} 位用户`;
  }
  
  return namesStr;
}

export default {
  getUserDisplayName,
  formatAuthorName,
  getUserDetailedDisplayName,
  formatUserListDisplay
};
