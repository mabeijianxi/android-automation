<h1 align="center">利用Jenkins玩转Android自动打包发包</h1>
###先看一眼效果图：<图1>
<h3 align="left">总体步骤可为：<h3>

<ol style="font-size:15px">
<li>下载新版Jenkins挂载到Tomcat</li>
<li>安装Jenkins里面需要用到的一些插件并且配置Jenkins参数</li>
<li>配置项目build.gradle里面的脚本</li>
<li>编写Python脚本拉取蒲公英上Apk二维码（可选）</li>
</ol>
<h3>正式开撸</h3>
<h4>一、下载新版Jenkins挂载到Tomcat：</h4>
到<a half="https://jenkins.io/">Jenkins</a>下载适合的版本后点击安装，之后在Tomcat的webapps目录下新建一个Jenkins目录，再把刚安装好的Jenkins目录打开找到war目录，拷贝目录下全部数据到webapps下新建的Jenkins目录中。还有种启动方式是通过命令启动jenkins.war就行了，```java -jar jenkins_located_path/jenkins.war```。我们可以先为工作空间配置个环境变量。<图8><图2></br>
我使用的是第一种方式，再启动Tomcat后访问<a half="http://localhost:8080/jenkins">http://localhost:8080/jenkins</a>就会进入引导进入页面，如果有选择安装插件界面进去后点击安装就行，一会儿就能进入主界面。<图3></br>
<h4>二、安装Jenkins里面需要用到的一些插件：</h4>
这里也没什么技术含量，系统管理->插件管理->管理插件->可选插件：
勾选如下插件：
<ol>
<li>Branch API Plugin</li>
<li>build timeout plugin</li>
<li>build-name-setter</li>
<li>Credentials Binding Plugin</li>
<li>description setter plugin</li>
<li>Dynamic Parameter Plug-in</li>
<li>Environment Injector Plugin</li>
<li>fir-plugin（可选）</li>
<li>Git plugin（可选）</li>
<li>GIT server Plugin(可选)</li>
<li>Gradle Plugin</li>
<li>Pipeline: Basic Steps</li>
<li>Pipeline: Build Step</li>
<li>Pipeline: Input Step</li>
<li>Pipeline: Nodes and Processes</li>
<li>Pipeline: Stage Step</li>
<li>Post-Build Script Plug-in</li>
<li>SSH Slaves plugin</li>
<li>Subversion Release Manager plugin(可选)</li>
<li>Timestamper</li>
<li>Workspace Cleanup Plugin</li>
<li>Subversion Plug-in(可选)</li>
</ol>
由于有些插件之间有依赖关系所以没全部列出来，如过有我问题可以对比我的截图。<图4><图5><图6><图7>。</br>

<h4>三、配置build.gradle：</h4>
上面都是枯燥的准备工作，好玩的才刚刚开始，下面的参数传入很有意思，也是我踩了很多坑以后想到的。
进入Android Studio->打开主Module的build.gradle：</br>
<ol>
<li>配置签名信息,不然打的包就没意义了</li>
<li>以参数化构建你想动态写入的数据。我自己需要动态写入的参数有versionName、打包时间戳、是来自Jenkjins运行还是我们本地打包的标识符，这里很重要，如果是来自Jenkins打包那么我们的生产路径肯定是服务器上的路径，否则是我们本地电脑上的路径。把这三个参数与其在本地的默认值定义在gradle.properties中，然后在build.gradle变能引用。</li>
<li>动态修改生产的Apk路径与名称，因为如果是Jenkins打包发包那么名称必须是Jenkins传递过来的，不能写死，且唯一，不然没法上传</li>
</ol>
废话不多说，程序员就哪需要看这么多文字，直接干代码（一下是项目中部分代码）：</br>


```
gradle.build:

def getDate() {
    def date = new Date()
    def formattedDate = date.format('yyyyMMddHHmm')
    return formattedDate
}
def verCode = 14
android {
    compileSdkVersion 22
    buildToolsVersion "23.0.3"
    signingConfigs {
        signingConfig {
            keyAlias 'xxx'
            keyPassword 'xxx'
            storeFile file('xxx')
            storePassword 'xxx'
        }
    }

    defaultConfig {
        applicationId "com.henanjianye.soon.communityo2o"
        minSdkVersion 14
        targetSdkVersion 22
        multiDexEnabled true
        versionCode verCode
        versionName APP_VERSION
        resValue("string", 'app_version', APP_VERSION)
        buildConfigField "boolean", "LEO_DEBUG", "true"
        buildConfigField 'String', 'API_SERVER_URL', RELEASE_API_SERVER_URL
        buildConfigField 'String', 'API_SERVER_URL_MALL', RELEASE_API_SERVER_URL_MALL
        signingConfig signingConfigs.signingConfig
    }
    buildTypes {
        release {
            buildConfigField 'String', 'API_SERVER_URL', RELEASE_API_SERVER_URL
            buildConfigField 'String', 'API_SERVER_URL_MALL', RELEASE_API_SERVER_URL_MALL
            buildConfigField 'String', 'IM_SERVER_HOST', RELEASE_IM_SERVER_HOST
            buildConfigField 'int', 'IM_SERVER_PORT', RELEASE_IM_SERVER_PORT
            buildConfigField "boolean", "LEO_DEBUG", RELEASE_LEO_DEBUG
            minifyEnabled true
            zipAlignEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
        debug {
            buildConfigField 'String', 'API_SERVER_URL', RELEASE_API_SERVER_URL
            buildConfigField 'String', 'API_SERVER_URL_MALL', RELEASE_API_SERVER_URL_MALL
            buildConfigField 'String', 'IM_SERVER_HOST', RELEASE_IM_SERVER_HOST
            buildConfigField 'int', 'IM_SERVER_PORT', RELEASE_IM_SERVER_PORT
            buildConfigField "boolean", "LEO_DEBUG", RELEASE_LEO_DEBUG
        }
    }
    dexOptions {
        javaMaxHeapSize "2g"
    }


    //渠道Flavors，我这里写了一些常用的
    productFlavors {
        commonsoon {
            manifestPlaceholders = [UMENG_CHANNEL_VALUE: "commonsoon"]
        }
        zhushou91 {
            manifestPlaceholders = [UMENG_CHANNEL_VALUE: "zhushou91"]
        }
    }
    allprojects {
        repositories {
            mavenCentral()
            maven { url "https://jitpack.io" }
        }
    }
    //修改生成的apk名字
    applicationVariants.all { variant ->
        variant.outputs.each { output ->
            def newName
            def timeNow
            def oldFile = output.outputFile
            def outDirectory = oldFile.parent

            if ("true".equals(IS_JENKINS)) {
                timeNow = JENKINS_TIME
                outDirectory = 'G:/Tomcat/webapps/jenkins/apk'
                newName = 'yj-android-v' +
                        APP_VERSION + '-' + variant.productFlavors[0].name + timeNow + '-' + variant.buildType.name + '.apk'
            } else {
                timeNow = getDate()
                if (variant.buildType.name.equals('debug')) {
                    newName = "yj-android-v${APP_VERSION}-debug.apk"
                } else {
                    newName = 'yj-android-v' +
                            APP_VERSION + '-' + variant.productFlavors[0].name + timeNow + '-' + variant.buildType.name + '.apk'
                }
            }

            output.outputFile = new File(outDirectory, newName)

        }
    }
}


gradle.properties:


RELEASE_API_SERVER_URL="http://o2o.yijiahn.com/jyo2o_web/"
RELEASE_API_SERVER_URL_MALL="http://mall.yijiahn.com/mall/"
RELEASE_IM_SERVER_HOST="chat.jianyezuqiu.cn"
RELEASE_IM_SERVER_PORT=5222
RELEASE_LEO_DEBUG=false

INSIDE_TEST_API_SERVER_URL="http://cso2o.yijiahn.com:8099/jyo2o_web/"
INSIDE_TEST_API_SERVER_URL_MALL="http://cso2o.yijiahn.com:8088/mall/"
INSIDE_TEST_IM_SERVER_HOST="cso2o.yijiahn.com"
INSIDE_TEST_IM_SERVER_PORT=5222
INSIDE_TEST_LEO_DEBUG=true

APP_VERSION=2.4.0
IS_JENKINS=false
JENKINS_TIME=''

```

<h4>四、配置Jenkins参数</h4>
回到主界面->系统管理->Global Tool Configuration：
配置好JDK与Gradle。由于我本地已安装好JDK与Gradle所以只需为其指定路径即可。<图9><图10></br>
然后回到主界面->新建->构建一个自由风格的项目->ok:</br>
<ol>
<li>勾选上参数化构建过程,先点击Choice可为其配置可选参数。我的项目需要配置的可选参数有API环境、打包渠道、是否来自Jenkins打包的标识。<图11>
<图12><图13><图14><图15></li>
<li>点击String Parameter,让使用者可以自定义显示在App上的版本号，方便测试。可以再添加一个可输入的标签，最后把这个标签加到构建页的构建名称中。<图16></li>
<li>点击Dynamic Parameter,注入Groovy脚本，主要是生产时间戳。<图17></li>
<li>如果是SVN用户可选择List SubVersion tags,然后写地址帐号密码等，这个选项可以让你选择打包SVN上不同版本的代码。如果是Git用户可参照<a src='http://birdinroom.blog.51cto.com/7740375/1404930'>http://birdinroom.blog.51cto.com/7740375/1404930</a> 上面的配置来拉取不同的版本。<图18><图21></li>
<li>勾选源码管理中自己所用的管理工具Git或者Subversion,填写好相关信息，当然我们的地址是动态的，所以需要引用上一步所选择的版本，如图。<图19></li>
<li>在构建环境中勾选上Set Build Name,主要是动态生成每次显示在构建页上的名称方便查看。<图20></li>
<li>在构建栏里面选择Invoke Gradle Script->选择配置好的Gradle Version->在Tasks中输入Grale命令（没了解过的建议先看下Grale的基本命令），这时候就可以用引用上面配置的一些参数了，这里可以用-P命令把参数出入，也可以更方便的把下面的Pass jod parameters as Gradle properties勾选上，其实内部也是用-Pkey=Value的命令->在Root Build   script中动态指定你项目的目录，为什么是动态的呢？这是因为我们上面提供了可选版本的功能，所以拉取的每个版本所放目录是不一样的，想要编译相应的版本就得动态指定编译目录。<图22> </li>
<li>上面的操作如果成功那么其实这时候构建已经可以在build.gradle所配置的输出路径中找到相应的Apk了，但是这还不够酷，我想把生产的Apk放到托管平台，这里推荐fir.im与蒲公英。如果选择fir.im那么本步骤略过，我个人推荐蒲公英，因为其可用命令行上传比较方（B）便(格)。下面是蒲公英上传的步骤。</br>
1)简单的实现方式：参照官方文档<a src='https://www.pgyer.com/doc/view/jenkins'>https://www.pgyer.com/doc/view/jenkins</a> 。这种方式可以可以简单的通过命令行上传，方便使用，且后续可以动态拿到Apk的下载连接，与最新版本的二维码。但是想要拿到每个版本的二维码确实不行的。其实上传成功后返回的json数据中Apk的下载地址与二维码地址是写死的一个短网址，后续说明解决办法。这里按照官方的步骤，如果是Linux
那么在增加构建步骤中选择Execute Shell,而Windows环境的需要先下载curl工具，然后选择Execute Windows batch command。get地址与使用方法都在里面<a src='http://www.2cto.com/os/201205/131164.html'>http://www.2cto.com/os/201205/131164.html</a>。 <图23></br>
需要注意这里的上传文件的名称也是动态引用的方式，因为每次生产的名称是唯一的。用过是Shell那么引用方式的$｛NAME｝,而batch那么引用方式是%NAME%。</br>
2）比较装逼的方式:我不只想要每个版本的下载长链接，我还想要每个版本二维码的长链接。但是就算同过浏览器打开最新上传的Apk地址，里面的二维码也只有短链接，不管是Apk的短链接还是二维码的它们其实是写死的，永远指向最新版的地址，这就有个问题，当在Jenkins中打开非最新版本的Apk地址或者二维码图片地址那么都会指向最新的，这就比较蛋疼了。经过仔细观察发现蒲公英Apk长链接生产的规则其实是固定字符串+appKey。Apk在返回的json串中可以找到。于是可以利用python脚本来执行上传，然后正则配置到AppKey，然后再拼上静态字符串就拿到了本次存放Apk的长链接。当然如果只是为了长链接用第一种方式即可。现在需要的是二维码的长链接，用Apk的长链接发起Http请求然后就可以拿到页面数据，通过正则匹配可以匹配到里面二维码的img标签地址，但是是短地址，蒲公英只有Apk才会在这个页面的img标签中返回长地址。于是我打了一个包名与签名同上传Apk相同的apk，但是里面没东西，大小只有几十K。在第一个Apk上传完成后马上上传这个小的Apk，这样再去拉取页面里面的img标签就可以得到二维码的长网址了。具体实现看下面python代码。</br>
<pre><code>
#coding: utf-8
import os
import re
import requests
import sys

if len(sys.argv) == 2:
    mainpath = sys.argv[-1]
else:
    exit()

temppath = r'G:\mydownload\GETUI_ANDROID_SDK\GETUI_ANDROID_SDK\Demo\PushDemo\yijia\temp.apk'

cmd = 'curl -F "file=@{path}" -F "uKey=xxx" -F "_api_key=xxx" http://www.pgyer.com/apiv1/app/upload'
content = os.popen(cmd.format(path=mainpath)).read()
print(content)

match = re.search('"appKey":"(\w+)"', content)

if match:
    appkey = match.group(1)

    content = os.popen(cmd.format(path=temppath)).read()

    url = 'http://static.pgyer.com/' + appkey
    html = requests.get(url).text

    match = re.search('http://static.pgyer.com/app/qrcodeHistory/\w+', html)
    if match:
        print('appKey#{soonAppkey}#appKeysoon#{soon}#soon'.format(soonAppkey=appkey,soon=match.group()))
    else:
        print('no qrcode')
</code></pre>
命令中执行如图代码：<图24>
</li>
<li>经过上面的操作后大业马上就成了，接下来就是收集成果的时候了，在增加构建后操作步骤中选择Set build description，Regular expression中填写正则，然后磕着Description中可以引用，这里去匹配的是构建日志中的内容，Description的内容将显示到构建页面。我们这里如果需要插入下载链接或者二维码的话那么就需要用到Html标签，这时候需要去先设置下。步骤：系统管理->Configure Global Security->	Markup Formatter->Safe HTML。如果是选择上面的简单实现方式那么Regular expression的正则可以用户："appKey":"（.*）","userKey",用过用我的pyhton那么正则可以是:appKey#(.*)#appKeysoon#(.*)#soon,然后在Description中通过\1或者\2引用即可。<图25><图26></li>
</ol>
<h4>四、打包喝咖啡</h4>
到这里那么最感动的时刻来了，轻轻的点击下保存按钮，这时候你会来到构建界面，轻击 Build with Parameters，就会出现这个界面<图27>。配置好参数，安下时代性的构建。从这一刻起如果测试要包你可以白他一眼，然后淡淡的说道:撸着呢，一边自己打去。
<h4>注意事项：</h4>
参数传递的时候Jenkins里面的参数名称需要与build.gradle里面的一直，不然没什么卵用。如<图28><图29>





