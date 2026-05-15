const fileSystem = {
  readFile: jest.fn(),
  writeFile: jest.fn(),
  readFileSync: jest.fn((path) => {
    const files = {
      '/mock/user.json': JSON.stringify({ id: 'test', name: 'Test' }),
    };
    return files[path] || null;
  }),
  writeFileSync: jest.fn(),
  existsSync: jest.fn((path) => path.includes('/mock/')),
  mkdirSync: jest.fn(),
  unlinkSync: jest.fn(),
  readdirSync: jest.fn(() => []),
};

global.fileSystem = fileSystem;
module.exports = fileSystem;