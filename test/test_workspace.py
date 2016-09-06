from unittest import TestCase

from ect.core.workflow import Workflow, OpStep, NodePort


class Workspace(object):
    def __init__(self, path):
        self._path = path
        self._workflow = Workflow('workspace-wf')

    @property
    def workflow(self) -> Workflow:
        """The Workspace's workflow."""
        return self._workflow

    def add_resource(self, name, op, **kwargs):
        step = OpStep(op, name)
        for k, v in kwargs.items():
            if k in step.input:
                port = step.input[k]
                # print(k,kwargs[k])
                node = self._workflow.find_node(v)
                if node:
                    port.source = node.output['return']
                else:
                    port.value = v
            else:
                raise ValueError('unknown parameter "%s"' % k)
        self._workflow.add_steps(step)
        self._workflow.op_meta_info.output[name] = step.op_meta_info.output['return']
        output_port = NodePort(self._workflow, name)
        output_port.source = step.output['return']
        self._workflow.output[name] = output_port


class WorkflowTest(TestCase):
    def test_example(self):
        import json
        ws = Workspace('/path')
        print("wf_1: " + json.dumps(ws.workflow.to_json_dict(), indent='  '))
        ws.add_resource('p', 'ect.ops.io.read_netcdf', file='2010_precipitation.nc')
        print("wf_2: " + json.dumps(ws.workflow.to_json_dict(), indent='  '))
        ws.add_resource('ts', 'ect.ops.timeseries.timeseries', ds='p', lat=53, lon=10)
        print("wf_3: " + json.dumps(ws.workflow.to_json_dict(), indent='  '))
