module.exports = function(grunt) {

  grunt.initConfig({
    jshint: {
      files: ['Gruntfile.js', 'js/base/**/*.js'],
      options: {
        globals: {
          jQuery: true
        }
      }
    },
    uglify:{
        default:{
            files : {
                'app/static/js/main.min.js' : [
                    'app/static/js/base/**/*.js',
                    'node_modules/gentelella/build/js/custom.js'
                ]
            }
        }
    },
    less:{
        default:{
            options:{
                sourceMap :false,
                compress: true,
                paths: ['app/static/vendors', 'app/static/less']
            },
            files: {'app/static/css/styles.css':'app/static/less/core.less'},
        }
    },
    cssmin: {
        default: {
            options:{
                sourceMap: true,
                report: true
            },
            files: {'app/static/css/style.min.css': ['app/static/css/styles.css']}
        }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-jshint');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-cssmin');

  grunt.registerTask('default', ['uglify', 'less', 'cssmin']);

};