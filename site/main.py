from flask import Flask, render_template, request, redirect, url_for
import urllib2
from docutils.core import publish_string
import ast
import json
import misaka
from misaka import HtmlRenderer, SmartyPants
from pygments import highlight, lexers, formatters
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class HighlighterRenderer(HtmlRenderer, SmartyPants):
    def block_code(self, text, lang):
        s = ''
        if not lang:
            lang = 'text'
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except:
            s += '<div class="highlight"><span class="err">Error: language "%s" is not supported</span></div>' % lang
            lexer = get_lexer_by_name('text', stripall=True)
        formatter = HtmlFormatter()
        s += highlight(text, lexer, formatter)
        return s

    def table(self, header, body):
        return '<table class="table">\n'+header+'\n'+body+'\n</table>'

renderer = HighlighterRenderer(flags=misaka.HTML_ESCAPE | misaka.HTML_HARD_WRAP | misaka.HTML_SAFELINK)
md = misaka.Markdown(renderer,
    extensions=misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS | misaka.EXT_TABLES | misaka.EXT_AUTOLINK | misaka.EXT_SPACE_HEADERS | misaka.EXT_STRIKETHROUGH | misaka.EXT_SUPERSCRIPT)


app = Flask(__name__)


@app.route('/')
def index():
    #linkList = "<li><a href='/article?url=https://raw.githubusercontent.com/alex/what-happens-when/master/README.rst' >What happens when you type google.com into your browser's address box and press enter?</a></li>\n"
    linkList = ''
    null = 'null'
    repoList = json.loads(urllib2.urlopen('https://api.github.com/repos/nickpetty/What-Happens-When/contents/articles').read())

    i = 0
    while i < len(repoList):
        if repoList[i]['download_url'] != 'null':
            url = repoList[i]['download_url']
            name = repoList[i]['name']
            li = '<li><a href="/article?url=%s">%s</a></li>\n' % (url, name)
            linkList += li
            i+=1

    return render_template('home.html', links=linkList)


@app.route('/article', methods=['GET'])
def article():
    if request.args.get('url')[-2:] == 'st':
        req = urllib2.urlopen(request.args.get('url'))
        html = publish_string(req.read().decode('utf8', 'ignore').encode('ascii', 'ignore'), writer_name='html')
    else:
        html = md.render(urllib2.urlopen(request.args.get('url')).read().decode('utf8'))
    return render_template('article.html', content=html)

@app.route('/test')
def test():
    return render_template('test.html')

app.run(host='0.0.0.0', port=80, debug=True)




