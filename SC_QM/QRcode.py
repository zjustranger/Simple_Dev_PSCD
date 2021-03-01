import qrcode
from PIL import Image
from PIL import ImageFilter
from PIL import ImageEnhance
from PIL import ImageDraw,ImageFont
import os
import datetime

tempdir = os.getcwd() + r'\temp\tempdata' + '\\'

# 图片宽高尺寸
def getImgSize(fname):
    imgObj = Image.open(fname)
    return imgObj.size

# 获取图片宽度
def getImgWidth(fname):
    imgObj = Image.open(fname)
    return imgObj.size[0]

# 获取图片高度
def getImgHeight(fname):
    imgObj = Image.open(fname)
    return imgObj.size[1]

'''
给图片加文字
生成一张blankimg空白图片，加上文字之后为fontimg图片,宽度为oldimg原始图片的宽度
'''
def imgAddFont(blankimg, oldimg, fontimg, text):
    Image.new("RGB", (getImgWidth(oldimg), 90), (255, 255, 255)).save(blankimg, "PNG");
    im = Image.open(blankimg)
    draw = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 16)
    draw.text((20, 0), text, fill='black', font=fnt)
    # im.show()
    im.save(fontimg)


'''
给图片加文字
生成一张blankimg空白图片，加上文字之后为fontimg图片,高度为oldimg原始图片的高度
'''
def imgAddFont2(blankimg, oldimg, fontimg, text):
    Image.new("RGB", (300, getImgHeight(oldimg)), (255, 255, 255)).save(blankimg, "PNG");
    im = Image.open(blankimg)
    draw = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc', 13)
    draw.text((20, 0), text, fill='black', font=fnt)
    # im.show()
    im.save(fontimg)


# imgAddFont(tempdir + 'blank.png', tempdir + 'qrcode.gif', tempdir + 'font.gif', 'Serial No: IT0004\nPart Number: 8753672\nOriginal Qty: 400')

'''
拼接图片，把上面生成的文字图片拼接到原图上面
生成一张宽度一致，高度为两张图片之和的空白长图
分别打开图片进行粘贴到空白长图里面
'''


def joinImg(fontimg, oldimg, newimg):
    w = getImgWidth(fontimg)
    fh = getImgHeight(fontimg)
    oh = getImgHeight(oldimg)

    blankLongImg = Image.new('RGBA', (w, fh + oh))  # 空白长图

    oldimg1 = Image.open(oldimg).resize((w, oh), Image.ANTIALIAS)
    blankLongImg.paste(oldimg1, (0, 0))

    fontimg1 = Image.open(fontimg).resize((w, fh), Image.ANTIALIAS)
    blankLongImg.paste(fontimg1, (0, oh))

    blankLongImg.save(newimg)
    # print('新拼接的图片：' + newimg)


# joinImg(tempdir + 'font.gif', tempdir + 'qrcode.gif', tempdir + 'new.gif')


'''
拼接图片，把上面生成的文字图片拼接到原图右面
生成一张高度一致，宽度为两张图片之和的空白长图
分别打开图片进行粘贴到空白长图里面
'''


def joinImg2(fontimg, oldimg, newimg):
    h = getImgHeight(fontimg)
    fw = getImgWidth(fontimg)
    ow = getImgWidth(oldimg)

    blankLongImg = Image.new('RGBA', (fw + ow, h))  # 空白长图

    oldimg1 = Image.open(oldimg).resize((ow, h), Image.ANTIALIAS)
    blankLongImg.paste(oldimg1, (0, 0))

    fontimg1 = Image.open(fontimg).resize((fw, h), Image.ANTIALIAS)
    blankLongImg.paste(fontimg1, (ow, 0))

    blankLongImg.save(newimg)
    # print('新拼接的图片：' + newimg)


def generate_qr_code(data):
    # 生成二维码
    qr = qrcode.QRCode(
        version = 1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=4,
        border=2
    )

    # 二维码内容
    # data = "|P|32237800|Q|100|V|AHFGA|N|20200423|S|SC0001|M|20200301|"
    qr.add_data(data)

    # 直接显示二维码
    img = qr.make_image()
    # img.show()
    # 保存二维码为文件
    img.save(tempdir + "qrcode.gif")

def generate_new_label_file(sn, partno, qty, dd, userid):
    # 拼接label内容
    label_content = '|S|' + str(sn) + '|P|' + str(partno) + '|Q|' + str(qty) + '|D|' + str(dd) + '|'

    # 产生QRcode文件qrcode.gif，存储在临时数据文件夹里
    generate_qr_code(label_content)

    # 产生文字图片font.gif, 存储在临时数据文件夹里
    imgAddFont2(tempdir + 'blank.png', tempdir + 'qrcode.gif', tempdir + 'font.gif',
               '序列号：' + str(sn) + '\n' + '物料号：' + str(partno) + '\n' + '拆分原始数量：' + str(qty) + '\n' + '过期日期：' + str(dd))

    # 拼接二维码和文字信息
    outputdir = os.getcwd() + r'\newlables' + '\\'
    outputlabelname = 'S_' + str(sn) + '_P_' + str(partno) + '_Q_' + str(qty) + '_' + str(userid) + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.gif'
    joinImg2(tempdir + 'font.gif', tempdir + 'qrcode.gif', outputdir + outputlabelname)

def manual_generate_QR_code(p, q, v, n, s, b, m, d, userid):
    label_content = '|P|{0}|Q|{1}|V|{2}|N|{3}|S|{4}|B|{5}|M|{6}|D|{7}|'.format(p, q, v, n, s, b, m, d)

    # 产生QRcode文件qrcode.gif，存储在临时数据文件夹里
    generate_qr_code(label_content)

    # 产生文字图片font.gif, 存储在临时数据文件夹里
    imgAddFont(tempdir + 'blank.png', tempdir + 'qrcode.gif', tempdir + 'font.gif',
               '序列号：' + str(s) + '\n' + '物料号：' + str(p) + '\n' + '原始数量：' + str(q) + '\n' + '过期日期：' + str(d))

    # 拼接二维码和文字信息
    outputdir = os.getcwd() + r'\newlables' + '\\'
    outputlabelname = 'S_' + str(s) + '_P_' + str(p) + '_Q_' + str(q) + '_' + str(userid) + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.gif'
    joinImg(tempdir + 'font.gif', tempdir + 'qrcode.gif', outputdir + outputlabelname)

def manual_generate_qr_code_new(p, q, v, n, s, b, m, d, descr, userid):
    label_content = '|P|{0}|Q|{1}|V|{2}|N|{3}|S|{4}|B|{5}|M|{6}|D|{7}|'.format(p, q, v, n, s, b, m, d)

    # 产生QRcode文件qrcode.gif，存储在临时数据文件夹里
    generate_qr_code(label_content)

    # 产生文字图片font.gif, 存储在临时数据文件夹里
    imgAddFont2(tempdir + 'blank.png', tempdir + 'qrcode.gif', tempdir + 'font.gif',
               '-------------------------------------------\n批次号：{}\n物料号：{}\n中文名称：{}\n包装数量：{}\n过期日期：{}\n序列号：{}\n-------------------------------------------'.format(b, p, descr, q, d, s))

    # 拼接二维码和文字信息
    outputdir = os.getcwd() + r'\newlables' + '\\'
    outputlabelname = 'S_' + str(s) + '_P_' + str(p) + '_Q_' + str(q) + '_' + str(
        userid) + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.gif'
    joinImg2(tempdir + 'font.gif', tempdir + 'qrcode.gif', outputdir + outputlabelname)


if __name__ == '__main__':
    manual_generate_qr_code_new('66666666', 100, 'TEST1', '20043001', 'IT001002', 'NN20200526-001', '20200330', '20200630', '测试物料号——牛奶500ml', 'cyang44')
    # generate_qr_code("|P|CC0200144||Q|100||S|DUMMY200601-267||B|XJP20200603-02-01||D|20201020|")
    # print(os.getcwd())