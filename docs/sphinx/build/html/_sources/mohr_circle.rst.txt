Mohr's circle
=============

Mohr's circle offers an intuitive way to visualize states of stress and stress transformations. The following interactive demonstration is intended to enhance one's understanding of Mohr's circle. Click on the example below to get started.
   
.. raw:: html

	 <iframe src="_static/mohr_circle/index.html" style="width:100%; height:100%; aspect-ratio: 16/8;" scrolling="no" frameborder="0"></iframe>

The example above considers a block subjected to a two-dimensional state of stress, illustrated on the right side of the screen. The different components of normal and shear stress (:math:`\sigma_x`, :math:`\sigma_y`, :math:`\tau_{xy} = \tau_{yx}`) acting on the grey block whose edges are aligned with the :math:`x`-:math:`y` coordinate axes can be adjusted using the three sliders in the top left corner of the screen. The orientation of the blue block whose edges are aligned with the :math:`x'`-:math:`y'` axes can be adjusted by clicking on the blue block and rotating it. The components of normal and shear stress acting on the blue block (:math:`\sigma_{x'}`, :math:`\sigma_{y'}`, :math:`\tau_{x'y'} = \tau_{y'x'}`) are determined according to the stress transformation equations:
	
.. math::

   \sigma_{x'} = \frac{\sigma_x + \sigma_y}{2} + \frac{\sigma_x - \sigma_y}{2} \cos (2 \theta) + \tau_{xy} \sin (2 \theta)
   
.. math::

   \sigma_{y'} = \frac{\sigma_x + \sigma_y}{2} - \frac{\sigma_x - \sigma_y}{2} \cos (2 \theta) - \tau_{xy} \sin (2 \theta)
   
.. math::

   \tau_{x'y'} = - \frac{\sigma_x - \sigma_y}{2} \sin (2 \theta) + \tau_{xy} \cos (2 \theta)

where :math:`\theta` measures the angle between the :math:`x` and :math:`x'` coordinate axes. Try rotating the blue block to see how the state of stress in the :math:`x'`-:math:`y'` coordinate frame changes.

Mohr's circle is displayed on the left side of the screen, illustrating the aforementioned states of stress in a two-dimensional diagram, with normal stress :math:`\sigma` measured on the horizontal axis and shear stress :math:`\tau` measured on the vertical axis. The red and blue dots respectively represent the states of stress corresponding to :math:`(\sigma_x,\tau_{xy})` and :math:`(\sigma_y,-\tau_{yx})`, whereas the magenta and purple dots represent the transformed states of stress corresponding to :math:`(\sigma_{x'},\tau_{x'y'})` and :math:`(\sigma_{y'},-\tau_{y'x'})`, respectively. The center of Mohr's circle is positioned along the :math:`\sigma` axis, and corresponds to the "average" normal stress:

.. math::

   \sigma_{\text{avg}} = \frac{\sigma_x + \sigma_y}{2}

Additionally, the radius of Mohr's circle can be determined by the Pythagorean theorem:

.. math::

   R = \sqrt{\left( \frac{\sigma_x - \sigma_y}{2} \right)^2 + \left( \tau_{xy} \right)^2}

Moreover, :math:`R` represents the magnitude of the maximum in-plane shear stress :math:`\tau_{\text{max in-plane}}` among all possible rotation angles :math:`\theta \in [-180^{\circ},+180^{\circ}]`.

.. note:: If the blue block is rotated by an angle of :math:`\theta`, then the angle measured between :math:`(\sigma_x,\tau_{xy})` and :math:`(\sigma_{x'},\tau_{x'y'})` on Mohr's circle will be :math:`2 \theta` (*twice* the rotation angle).

For any state of stress characterized by :math:`\sigma_x`, :math:`\sigma_y`, and :math:`\tau_{xy}`, it is always possible to find a particular rotation angle :math:`\theta_p` for which :math:`\sigma_{x'}`, :math:`\sigma_{y'}` correspond to the principal stresses :math:`\sigma_{1,2} = \sigma_{\text{avg}} \pm R`. In particular:

.. math::

   \tan (2 \theta_p) = \frac{\tau_{xy}}{(\sigma_x - \sigma_y)/2}

Try to prove this to yourself by changing the values of :math:`\sigma_x`, :math:`\sigma_y`, :math:`\tau_{xy}` and attempting to find the value of :math:`\theta_p` for which :math:`\tau_{x'y'} = 0`, and notice how the plotted points for :math:`\sigma_{x'}`, :math:`\sigma_{y'}` in Mohr's circle appear on the normal stress axis.
