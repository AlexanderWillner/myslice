from unfold.plugin import Plugin

class ResourcesSelected(Plugin):

    def template_file (self):
        return "resources_selected.html"

    def requirements (self):
        reqs = {
            'js_files' : [ "js/resources_selected.js" ] ,
            'css_files': [ "css/resources_selected.css" ],
            }
        return reqs

    def json_settings_list (self):
        return ['plugin_uuid', 'domid', 'resource_query_uuid', 'lease_query_uuid']

    def export_json_settings (self):
        return True