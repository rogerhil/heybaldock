from random import choice, randint
import Image, ImageDraw, ImageFont, sha
from decapole.settings import MEDIA_ROOT, SECRET_KEY

class Captcha:
   
    def generate_image(self, ipAddress):
        
        num_numbers = randint(1, 4)
        num_letters = 5 - num_numbers
        tipo_validacao = randint(0,1)
        pergunta=""
       
        imgtextL = ''.join([choice('QWERTYUOPASDFGHJKLZXCVBNM') for i in range(num_letters)])
        imgtextN = ''.join([choice('123456789') for i in range(num_numbers)])

        SALT = SECRET_KEY[:20]
        imgtext = ''.join([choice(imgtextL + imgtextN) for i in range(5)])
        im=Image.open(MEDIA_ROOT + 'images/jpg/captcha.jpg')
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype("/media/font/yellow_submarine.ttf", 30)
        draw.text((28,10),imgtext, font=font, fill=(255,255,255))
        temp = MEDIA_ROOT + "images/temp/" + ipAddress + '.jpg'
        tempname = ipAddress + '.jpg'
        im.save(temp, "JPEG")
       
        if tipo_validacao == 0:
            pergunta="n&uacute;meros"
            imghash = sha.new(SALT+imgtextN).hexdigest()
        if tipo_validacao == 1:
            pergunta="letras"
            imghash = sha.new(SALT+imgtextL).hexdigest()
        return {'captcha_img_name':tempname, 'hash_code_captcha':imghash, 'tipo_validacao':pergunta}

def index(request):
        if request.POST:
            data = request.POST.copy()
            SALT = SECRET_KEY[:20]

            # does the captcha math ?
            if data['hash_code_captcha'] == sha.new(SALT+data['imgtext']).hexdigest():
                return render_to_response('cadastro/formularioCadastro2.htm')
            else:
                c = Captcha()
                dados = c.gerarImagem(request.META['REMOTE_ADDR'])
                return render_to_response('cadastro/index.htm', dados)
        # no post data, show the form
        else:
            c = Captcha()
            dados = c.gerarImagem(request.META['REMOTE_ADDR'])
            return render_to_response('cadastro/index.htm', dados)

"""
<tr>
    <td width="193" align="center" height="77" valign="middle">
  <input type="hidden" value="{{hash_code_captcha }}" name="hash_code_captcha">
  <p><src="/media/images/temp/{{captcha_img_name}}"></p>
    </td>
    <td width="220" align="center" height="77" valign="middle">
  <input type="text" name="imgtext" size="10" >
 </td>
  </tr>
"""