# android-automation
利用Jenkins实现Android自动打包发包

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
gradle.build:

```
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
```</br>
gradle.properties:</br>
```
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










<h4>三、配置Jenkins参数</h4>
回到主界面->系统管理->Global Tool Configuration：
配置好JDK与Gradle。由于我本地已安装好JDK与Gradle所以只需为其指定路径即可。<图9><图10></br>
然后回到主界面->新建->构建一个自由风格的项目->ok:



