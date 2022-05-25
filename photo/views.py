from distutils.command.upload import upload
from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm, DocumentNameForm
from django.views import generic
from pathlib import Path
import shutil

class PhotoTop(generic.TemplateView):
    template_name = 'home.html'

    def get(self, request, *args, **kwargs):
        # ログイン情報が入っていなければ、リダイレクト
        if not request.user.is_authenticated:
            return redirect('account:login')
        else:
            photos = Document.objects.filter(user_id=request.user.pk).all()
            params = {
                'documents': photos,
            }
            return render(request, self.template_name, context=params)
    
    def post(self, request, *args, **kwargs):
        # データベースの削除処理
        delete_photo_id = request.POST['photo_id']
        Document.objects.filter(pk=delete_photo_id).delete()
        photos = Document.objects.filter(user_id=request.user.pk).all()

        # 保存したファイルの削除処理
        delete_photo_path = str(Path(__file__).parent.parent) + request.POST['photo_url']
        delete_photo_dir  = delete_photo_path[:-1 * len(delete_photo_path.split('/')[-1])]
        shutil.rmtree(delete_photo_dir)

        params = {
            'documents': photos,
            'message': '正常に削除されました'
        }
        return render(request, self.template_name, context=params)
            
class PhotoUpload(generic.TemplateView):
    template_name = 'upload.html'

    def get(self, request, *args, **kwargs):
        # ログイン情報が入っていなければ、リダイレクト
        if not request.user.is_authenticated:
            return redirect('account:login')
        else:
            form = DocumentForm()
            params = {
                'form': form,
            }
            return render(request, self.template_name, context=params)

    def post(self, request, *args, **kwargs):
        if request.FILES:
            # ファイルの拡張子が画像かどうかを判定
            upload_document_name = request.FILES['document'].name
            if upload_document_name.split('.')[-1] in ['jpg', 'JPG', 'jpeg', 'png']:
                document_params = {
                    'filename': upload_document_name,
                    'email': request.user.email,
                    'user_id': request.user.pk,
                }
                form = DocumentNameForm(document_params, request.FILES)
                if form.is_valid():
                    form.save()
                    return redirect('photo:home')
                else:
                    params = {
                        'message': 'ファイルが見つかりませんでした',
                        'form': DocumentForm(),
                    }
                    return render(request, self.template_name, context=params)
            else:
                params = {
                    'message': 'アップロードできる拡張子は、"jpg", "jpeg", "png" のいずれかです',
                    'form': DocumentForm(),
                }
                return render(request, self.template_name, context=params)
        else:
            params = {
                'message': 'ファイルが見つかりませんでした',
                'form': DocumentForm(),
            }
            return render(request, self.template_name, context=params)