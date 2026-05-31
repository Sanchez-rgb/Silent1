"""测试 Word 转 PDF API"""
import requests
import os
import time

BASE_URL = 'http://localhost:8000'

def test_single_conversion():
    """测试单个文件转换"""
    print('\n' + '='*60)
    print('测试单个文件转换...')
    print('='*60)
    
    test_file = os.path.join('test_data', 'test_file_1.docx')
    
    if not os.path.exists(test_file):
        print(f'错误: 测试文件不存在 {test_file}')
        return False
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(f'{BASE_URL}/convert/single', files=files)
        
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            output_file = 'test_output_single.pdf'
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f'✅ 转换成功! 输出文件: {output_file}')
            return True
        else:
            print(f'❌ 转换失败: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ 请求失败: {e}')
        return False


def test_batch_conversion():
    """测试批量转换"""
    print('\n' + '='*60)
    print('测试批量转换...')
    print('='*60)
    
    test_files = [
        os.path.join('test_data', 'test_file_1.docx'),
        os.path.join('test_data', 'test_file_2.docx'),
        os.path.join('test_data', 'test_file_3.docx')
    ]
    
    # 检查文件是否存在
    for f in test_files:
        if not os.path.exists(f):
            print(f'错误: 测试文件不存在 {f}')
            return False
    
    try:
        files = []
        for f in test_files:
            files.append(('files', open(f, 'rb')))
        
        response = requests.post(f'{BASE_URL}/convert/batch', files=files)
        
        # 关闭文件句柄
        for _, f in files:
            f.close()
        
        print(f'状态码: {response.status_code}')
        
        if response.status_code == 200:
            output_file = 'test_output_batch.zip'
            with open(output_file, 'wb') as f:
                f.write(response.content)
            print(f'✅ 批量转换成功! 输出文件: {output_file}')
            return True
        else:
            print(f'❌ 批量转换失败: {response.text}')
            return False
            
    except Exception as e:
        print(f'❌ 请求失败: {e}')
        return False


if __name__ == '__main__':
    print('Word 转 PDF 服务测试')
    print(f'服务地址: {BASE_URL}')
    print('\n请确保服务正在运行!')
    print('如果服务未运行，请先执行: python main.py')
    
    # 等待服务启动
    try:
        input('\n按回车键开始测试 (确保服务已启动)...')
        
        print('\n正在检查服务是否可用...')
        health = requests.get(f'{BASE_URL}/docs')
        print('✅ 服务可用!')
        
        # 运行测试
        results = []
        results.append(test_single_conversion())
        results.append(test_batch_conversion())
        
        print('\n' + '='*60)
        print('测试总结:')
        print(f'总测试数: {len(results)}')
        print(f'通过: {sum(results)}')
        print(f'失败: {len(results) - sum(results)}')
        print('='*60)
        
    except requests.exceptions.ConnectionError:
        print('\n❌ 无法连接到服务，请确保服务正在运行!')
        print('请运行: python main.py')
    except Exception as e:
        print(f'\n❌ 测试过程出错: {e}')
